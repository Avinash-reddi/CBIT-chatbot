import random
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response as DRFResponse

from chatbot.models import (
    Category, Intent, Pattern, Response,
    ChatSession, ChatMessage, FallbackLog,
)
from chatbot.services.intent_matcher import IntentMatcher
from chatbot.services.context_resolver import resolve_context
from chatbot.services.fallback_learner import (
    learn_from_fallback, escalate_fallback, get_learning_stats,
)
from .serializers import (
    CategorySerializer, IntentListSerializer, IntentDetailSerializer,
    PatternSerializer, ResponseSerializer,
    ChatMessageSerializer, ChatSessionListSerializer,
    ChatInputSerializer, FallbackLogSerializer,
)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ── Public Chat Endpoints ──────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_message(request):
    serializer = ChatInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_text = serializer.validated_data["message"]
    session_id = serializer.validated_data.get("session_id")

    if session_id:
        try:
            session = ChatSession.objects.get(session_id=session_id, is_active=True)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(
                user_ip=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
    else:
        session = ChatSession.objects.create(
            user_ip=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    ChatMessage.objects.create(session=session, sender="user", text=user_text)

    # ── Context Resolution: two-pass matching strategy ──
    # Pass 1: Try matching the original query without context
    matcher = IntentMatcher()
    result = matcher.match(user_text)

    # Pass 2: If low confidence AND it's a follow-up, try with context
    ctx = resolve_context(user_text, session)
    context_desc = None

    if ctx["is_follow_up"]:
        should_try_context = False

        if ctx.get("has_pronoun"):
            # Pronouns (it, its, that, this) NEED context resolution
            # because the query can't stand alone. Always try context.
            should_try_context = True
        elif not result["intent"] or result["confidence"] < matcher.CONFIDENCE_THRESHOLD:
            # No pronoun, but the query failed to match on its own.
            # Try context enrichment as a fallback.
            should_try_context = True

        if should_try_context:
            resolved_text = ctx["resolved_text"]
            context_result = matcher.match(resolved_text)

            if context_result["intent"] and (
                not result["intent"]
                or context_result["confidence"] > result["confidence"]
            ):
                result = context_result
                context_desc = ctx.get("context_description")
        else:
            # Original matched well and no pronouns - just note context
            context_desc = ctx.get("context_description")

    corrected_input = result.get("corrected_input", user_text)
    was_corrected = corrected_input.lower().strip() != user_text.lower().strip()

    if result["intent"]:
        # ── Confident match ──
        responses = result["intent"].responses.filter(is_active=True)
        if responses.exists():
            reply_text = random.choice(list(responses)).text
        else:
            reply_text = "I found a match but don't have a response configured. Please contact the college office."

        # Prepend context/correction notice
        prefix_parts = []
        if ctx["is_follow_up"] and context_desc:
            prefix_parts.append(f"({context_desc})")
        if was_corrected and not ctx["is_follow_up"]:
            prefix_parts.append(f'I understood your question as "{corrected_input}"')

        if prefix_parts:
            prefix = "\n".join(prefix_parts)
            reply_text = f"{prefix}\n\n{reply_text}"

        ChatMessage.objects.create(
            session=session,
            sender="bot",
            text=reply_text,
            matched_intent=result["intent"],
            confidence_score=result["confidence"],
        )

        related_intents = (
            result["intent"]
            .category.intents.filter(is_active=True)
            .exclude(id=result["intent"].id)[:3]
        )
        suggestions = []
        for ri in related_intents:
            first_pattern = ri.patterns.first()
            if first_pattern:
                suggestions.append(first_pattern.text)

        return DRFResponse({
            "session_id": str(session.session_id),
            "reply": reply_text,
            "matched_intent": result["intent"].tag,
            "confidence": result["confidence"],
            "corrected_input": corrected_input if was_corrected else None,
            "context_used": context_desc,
            "is_follow_up": ctx["is_follow_up"],
            "suggestions": suggestions,
        })

    elif result.get("is_clarification") and result.get("suggestions"):
        # ── Low confidence - ask follow-up question ──
        suggestion_tags = result["suggestions"]
        clarification_intents = Intent.objects.filter(
            tag__in=suggestion_tags, is_active=True
        ).select_related("category")

        options = []
        suggestion_patterns = []
        for ci in clarification_intents:
            desc = ci.description or ci.tag.replace("_", " ").title()
            options.append(f"- {desc}")
            first_pattern = ci.patterns.first()
            if first_pattern:
                suggestion_patterns.append(first_pattern.text)

        if options:
            clarify_text = "I'm not quite sure what you're asking. Did you mean one of these?\n"
            clarify_text += "\n".join(options)
            clarify_text += "\n\nPlease choose one or rephrase your question."
        else:
            clarify_text = (
                "I partially understood your question but I'm not sure. "
                "Could you please be more specific? You can ask me about "
                "admissions, courses, fees, exam schedules, placements, or campus facilities."
            )

        prefix_parts = []
        if ctx["is_follow_up"] and context_desc:
            prefix_parts.append(f"({context_desc})")
        if was_corrected:
            prefix_parts.append(f'I interpreted your input as "{corrected_input}"')
        if prefix_parts:
            clarify_text = "\n".join(prefix_parts) + "\n\n" + clarify_text

        ChatMessage.objects.create(
            session=session,
            sender="bot",
            text=clarify_text,
            confidence_score=result["confidence"],
        )

        return DRFResponse({
            "session_id": str(session.session_id),
            "reply": clarify_text,
            "matched_intent": None,
            "confidence": result["confidence"],
            "corrected_input": corrected_input if was_corrected else None,
            "context_used": context_desc,
            "is_follow_up": ctx["is_follow_up"],
            "suggestions": suggestion_patterns,
        })

    else:
        # ── No match - fallback ──
        fallback_reply = (
            "I'm sorry, I couldn't understand your question. "
            "Could you please rephrase it? You can ask me about "
            "admissions, courses, fees, exam schedules, placements, or campus facilities."
        )

        if was_corrected:
            fallback_reply = (
                f'I tried interpreting your input as "{corrected_input}" '
                f"but still couldn't find a match.\n\n"
                "Could you please rephrase your question? I can help with "
                "admissions, courses, fees, exam schedules, placements, or campus facilities."
            )

        if ctx["is_follow_up"] and context_desc:
            fallback_reply = (
                f"({context_desc})\n\n"
                "I couldn't find specific information for that follow-up. "
                "Could you please be more specific? For example, try asking "
                "the full question like 'What is the B.Tech fee structure?'"
            )

        ChatMessage.objects.create(
            session=session,
            sender="bot",
            text=fallback_reply,
            confidence_score=0.0,
        )
        FallbackLog.objects.create(user_message=user_text, session=session)

        return DRFResponse({
            "session_id": str(session.session_id),
            "reply": fallback_reply,
            "matched_intent": None,
            "confidence": 0.0,
            "corrected_input": corrected_input if was_corrected else None,
            "context_used": context_desc,
            "is_follow_up": ctx["is_follow_up"],
            "suggestions": [],
        })


@api_view(["POST"])
@permission_classes([AllowAny])
def create_session(request):
    session = ChatSession.objects.create(
        user_ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    return DRFResponse({"session_id": str(session.session_id)}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def session_history(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return DRFResponse({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return DRFResponse({"messages": serializer.data})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_categories(request):
    categories = Category.objects.filter(is_active=True)
    serializer = CategorySerializer(categories, many=True)
    return DRFResponse(serializer.data)


# ── Admin Intent CRUD ──────────────────────────────────────


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class IntentViewSet(viewsets.ModelViewSet):
    queryset = Intent.objects.select_related("category").prefetch_related("patterns", "responses")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return IntentListSerializer
        return IntentDetailSerializer


class PatternViewSet(viewsets.ModelViewSet):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
    permission_classes = [IsAdminUser]


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAdminUser]


# ── Admin Analytics ────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    today = timezone.now().date()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    top_intents = list(
        ChatMessage.objects.filter(matched_intent__isnull=False)
        .values("matched_intent__tag")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    daily_messages = list(
        ChatMessage.objects.filter(timestamp__gte=thirty_days_ago)
        .annotate(date=TruncDate("timestamp"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    for item in daily_messages:
        item["date"] = item["date"].isoformat()

    category_distribution = list(
        ChatMessage.objects.filter(matched_intent__isnull=False)
        .values("matched_intent__category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    learning = get_learning_stats()

    data = {
        "total_sessions": ChatSession.objects.count(),
        "total_messages": ChatMessage.objects.count(),
        "total_intents": Intent.objects.filter(is_active=True).count(),
        "total_unanswered": FallbackLog.objects.filter(resolved=False).count(),
        "messages_today": ChatMessage.objects.filter(
            timestamp__date=today
        ).count(),
        "learned_intents": learning["learned"],
        "learning_rate": learning["learning_rate"],
        "escalated_count": learning["escalated"],
        "top_intents": top_intents,
        "category_distribution": category_distribution,
        "daily_messages": daily_messages,
    }
    return DRFResponse(data)


# ── Admin Chat History ─────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_chat_history(request):
    sessions = ChatSession.objects.all()
    serializer = ChatSessionListSerializer(sessions, many=True)
    return DRFResponse(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_session_detail(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return DRFResponse({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return DRFResponse({
        "session_id": str(session.session_id),
        "started_at": session.started_at,
        "messages": serializer.data,
    })


# ── Admin Fallbacks ────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_fallbacks(request):
    filter_status = request.query_params.get("status")
    fallbacks = FallbackLog.objects.select_related("session", "learned_intent")

    if filter_status == "pending":
        fallbacks = fallbacks.filter(resolved=False)
    elif filter_status == "resolved":
        fallbacks = fallbacks.filter(resolved=True)
    elif filter_status == "escalated":
        fallbacks = fallbacks.exclude(assigned_department="")

    serializer = FallbackLogSerializer(fallbacks, many=True)
    return DRFResponse(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def resolve_fallback(request, pk):
    try:
        fallback = FallbackLog.objects.get(pk=pk)
    except FallbackLog.DoesNotExist:
        return DRFResponse({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    fallback.resolved = True
    fallback.resolved_at = timezone.now()
    fallback.resolved_by = request.user.username
    fallback.save()
    return DRFResponse({"status": "resolved"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def answer_fallback(request, pk):
    """
    Admin provides an answer to a fallback query.
    This auto-creates a new intent so the bot learns the answer.
    """
    admin_response = request.data.get("response", "").strip()
    category_id = request.data.get("category_id")
    department = request.data.get("department", "")

    if not admin_response:
        return DRFResponse(
            {"error": "Response text is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = learn_from_fallback(
        fallback_id=pk,
        admin_response=admin_response,
        category_id=category_id,
        assigned_department=department,
        resolved_by=request.user.username,
    )

    if "error" in result:
        return DRFResponse(result, status=status.HTTP_400_BAD_REQUEST)

    return DRFResponse(result, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def escalate_fallback_view(request, pk):
    """Escalate a fallback query to a specific department."""
    department = request.data.get("department", "").strip()
    if not department:
        return DRFResponse(
            {"error": "Department is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = escalate_fallback(
        fallback_id=pk,
        department=department,
        escalated_by=request.user.username,
    )

    if "error" in result:
        return DRFResponse(result, status=status.HTTP_400_BAD_REQUEST)

    return DRFResponse(result)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def department_list(request):
    """Return the list of departments for escalation."""
    return DRFResponse(
        [{"code": code, "name": name}
         for code, name in FallbackLog.DEPARTMENT_CHOICES]
    )
