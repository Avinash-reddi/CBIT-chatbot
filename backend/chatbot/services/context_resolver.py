"""
Conversation context resolver for follow-up questions.

Tracks the conversation topic within a session and resolves
pronouns/references like "it", "its", "that course" using
the session's message history.

Flow:
1. Load last matched intent + user messages from the session
2. Detect if the new message is a follow-up (pronouns, vague, short)
3. Extract topic keywords from conversation history
4. Rewrite the query by injecting context keywords
5. Return the enriched query for intent matching
"""

import re
from chatbot.models import ChatMessage


# ── Pronouns that refer back to a previous topic ──────────────

PRONOUNS = {"it", "its", "that", "this", "those", "these", "the"}

# Referential phrases (with the pronoun/reference included)
REFERENCE_PATTERNS = [
    r"\bits\b",           # "its fees", "what is its placement"
    r"\bit\b",            # "does it have", "is it good"
    r"\bthat\s+\w+",     # "that course", "that branch"
    r"\bthis\s+\w+",     # "this course", "this department"
    r"\bthe\s+same\b",   # "the same"
    r"\babout\s+it\b",   # "tell me about it"
    r"\bfor\s+it\b",     # "fees for it"
    r"\bof\s+it\b",      # "details of it"
    r"\bfor\s+that\b",   # "fees for that"
    r"\bof\s+that\b",    # "details of that"
    r"\bthere\b",        # "is there wifi", "are there sports"
]

# Phrases that start follow-up questions
FOLLOW_UP_STARTERS = [
    "what about", "how about", "and what about", "and how about",
    "tell me about its", "what is its", "what are its", "how is its",
    "and the", "and its", "also tell",
    "what about the", "how about the",
    "more about", "tell more", "more details", "more info",
    "anything else about", "also", "and",
]

# ── Intent tag → human-readable topic keywords ───────────────
# These keywords get injected into the rewritten query so the
# intent matcher can find the right combined match.

INTENT_TOPIC_KEYWORDS = {
    # General
    "greeting": [],
    "goodbye": [],
    "thanks": [],
    "bot_name": [],
    "college_info": ["cbit", "college"],
    "contact_info": ["contact", "college"],
    "college_address": ["cbit", "college", "address"],
    "college_timings": ["college", "timings"],

    # Admissions & Courses
    "admission_process": ["admission"],
    "courses_offered": ["courses"],
    "eligibility_criteria": ["eligibility"],
    "btech_cse": ["b.tech", "cse", "computer science"],
    "admission_dates": ["admission", "dates"],
    "documents_required": ["admission", "documents"],
    "lateral_entry": ["lateral entry", "diploma"],

    # Fees & Scholarships
    "fee_structure": ["fees", "fee structure"],
    "hostel_fees": ["hostel", "fees"],
    "scholarship_info": ["scholarship"],
    "payment_methods": ["fee", "payment"],

    # Exams & Schedules
    "exam_schedule": ["exam", "schedule"],
    "academic_calendar": ["academic", "calendar"],
    "internal_marks": ["internal", "marks"],
    "attendance_rules": ["attendance"],

    # Placements
    "placement_stats": ["placement", "statistics"],
    "top_recruiters": ["placement", "companies", "recruiters"],
    "average_package": ["placement", "salary", "package"],
    "placement_process": ["placement", "process"],
    "internships": ["internship"],

    # Campus & Facilities
    "campus_facilities": ["campus", "facilities"],
    "library": ["library"],
    "hostel": ["hostel"],
    "sports": ["sports"],
    "labs": ["labs", "laboratory"],
    "transportation": ["transport", "bus"],
    "canteen": ["canteen", "food"],
    "wifi": ["wifi", "internet"],
}

# ── Specific entity keywords to extract from user messages ────
# These are domain-specific nouns that carry topic meaning.

ENTITY_KEYWORDS = {
    "b.tech", "btech", "m.tech", "mtech", "mba",
    "cse", "ece", "eee", "mechanical", "civil", "electrical", "electronics",
    "computer science", "information technology",
    "admission", "admissions", "course", "courses",
    "fees", "fee", "hostel", "scholarship",
    "exam", "exams", "placement", "placements",
    "library", "sports", "canteen", "transport", "wifi",
    "internship", "attendance", "marks", "salary", "package",
    "campus", "facilities", "lab", "labs",
}


def _extract_entities_from_text(text):
    """Extract domain-specific entity keywords from a text string."""
    text_lower = text.lower()
    found = set()
    for entity in ENTITY_KEYWORDS:
        if entity in text_lower:
            found.add(entity)
    return found


def _is_follow_up(text):
    """
    Detect if the user message is likely a follow-up question.

    Returns a tuple (is_followup: bool, has_pronoun: bool, cleaned_text: str)
    - is_followup: True if follows from previous context
    - has_pronoun: True if contains a pronoun/reference that NEEDS resolution
      (it, its, that, this). This signals the query cannot stand alone.
    """
    text_lower = text.lower().strip()
    has_pronoun = False

    # Check for pronoun reference patterns
    for pattern in REFERENCE_PATTERNS:
        if re.search(pattern, text_lower):
            has_pronoun = True
            return True, True, text_lower

    # Check for follow-up starters (no pronoun, but contextual)
    for starter in FOLLOW_UP_STARTERS:
        if text_lower.startswith(starter):
            return True, False, text_lower

    # Very short messages (1-3 words) that are topic-only
    words = text_lower.split()
    if len(words) <= 3:
        has_question_word = any(w in {"what", "how", "when", "where", "why", "which"} for w in words)
        has_topic_word = bool(_extract_entities_from_text(text_lower))
        if has_topic_word and not has_question_word:
            return True, False, text_lower

    return False, False, text_lower


def _get_session_context(session, lookback=4):
    """
    Build conversation context from the session's most recent messages.

    Only looks at the last few messages to keep context focused
    on the current topic (not the entire session history).

    Returns a dict with:
    - last_intent_tag: str or None
    - last_category: str or None
    - topic_keywords: list of str (from last matched intent only)
    - entity_keywords: set of str (from last user message only)
    - last_user_text: str or None
    """
    recent_messages = list(
        ChatMessage.objects.filter(session=session)
        .select_related("matched_intent", "matched_intent__category")
        .order_by("-timestamp")[:lookback]
    )

    # Reverse to get chronological order
    recent_messages.reverse()

    context = {
        "last_intent_tag": None,
        "last_category": None,
        "topic_keywords": [],
        "entity_keywords": set(),
        "last_user_text": None,
    }

    # Find the LAST bot message with a matched intent (most recent topic)
    last_bot_intent = None
    for msg in reversed(recent_messages):
        if msg.sender == "bot" and msg.matched_intent:
            last_bot_intent = msg
            break

    if last_bot_intent:
        context["last_intent_tag"] = last_bot_intent.matched_intent.tag
        context["last_category"] = last_bot_intent.matched_intent.category.name
        tag = last_bot_intent.matched_intent.tag
        if tag in INTENT_TOPIC_KEYWORDS:
            context["topic_keywords"] = INTENT_TOPIC_KEYWORDS[tag]

    # Find the LAST user message (the one that led to the current topic)
    for msg in reversed(recent_messages):
        if msg.sender == "user":
            context["last_user_text"] = msg.text
            # Only extract entities from this most recent user message
            context["entity_keywords"] = _extract_entities_from_text(msg.text)
            break

    return context


def _rewrite_with_context(user_text, context):
    """
    Rewrite the user query by replacing pronouns/references with
    actual topic keywords from conversation context.

    Strategy: the user's NEW keywords take priority (placed first),
    and context keywords are appended to support matching.

    Returns (rewritten_text, context_description) tuple.
    context_description is a human-readable note about what context was used,
    or None if no rewriting happened.
    """
    text_lower = user_text.lower().strip()
    topic_words = context["topic_keywords"]
    entities = context["entity_keywords"]

    if not topic_words and not entities:
        return user_text, None

    # Build a SHORT, focused context injection (max 2 keywords).
    # Prefer specific entities the user mentioned (e.g., "b.tech")
    # over generic intent topic words (e.g., "computer science").
    entity_list = [e for e in entities if e.lower() not in text_lower]
    topic_list = [t for t in topic_words if t.lower() not in text_lower]

    # Entities first (user's own words are most specific), then topics
    candidates = entity_list + topic_list
    # Deduplicate while preserving order
    seen = set()
    inject_words = []
    for w in candidates:
        if w.lower() not in seen:
            seen.add(w.lower())
            inject_words.append(w)

    # Limit to 2 keywords to avoid overpowering the user's new query
    inject_words = inject_words[:2]

    if not inject_words:
        return user_text, None

    inject_str = " ".join(inject_words)

    # Strategy 1: Replace pronoun references with topic keywords
    rewritten = text_lower
    pronoun_replaced = False

    for pronoun in ["its", "it", "that", "this"]:
        pattern = rf"\b{pronoun}\b"
        if re.search(pattern, rewritten):
            rewritten = re.sub(pattern, inject_str, rewritten, count=1)
            pronoun_replaced = True
            break

    # Strategy 2: If no pronoun found, APPEND context to the end
    # (user's actual query stays first for priority in matching)
    if not pronoun_replaced:
        rewritten = f"{rewritten} {inject_str}"

    # Build a readable context description
    intent_tag = context["last_intent_tag"]
    if intent_tag:
        topic_name = intent_tag.replace("_", " ").title()
        context_desc = f"Continuing from: {topic_name}"
    else:
        context_desc = f"Based on previous context: {inject_str}"

    return rewritten.strip(), context_desc


def resolve_context(user_text, session):
    """
    Main entry point for context resolution.

    Given a user message and session, determines if the message is a
    follow-up question and rewrites it with conversation context.

    Returns a dict with:
    - original_text: str (the raw user input)
    - resolved_text: str (rewritten with context, or original if no follow-up)
    - is_follow_up: bool
    - context_description: str or None (human-readable context note)
    - last_intent_tag: str or None
    """
    # Check if there's any conversation history in this session
    msg_count = ChatMessage.objects.filter(session=session).count()

    if msg_count == 0:
        return {
            "original_text": user_text,
            "resolved_text": user_text,
            "is_follow_up": False,
            "has_pronoun": False,
            "context_description": None,
            "last_intent_tag": None,
        }

    is_followup, has_pronoun, cleaned_text = _is_follow_up(user_text)

    if not is_followup:
        context = _get_session_context(session)
        return {
            "original_text": user_text,
            "resolved_text": user_text,
            "is_follow_up": False,
            "has_pronoun": False,
            "context_description": None,
            "last_intent_tag": context["last_intent_tag"],
        }

    context = _get_session_context(session)

    if not context["last_intent_tag"]:
        return {
            "original_text": user_text,
            "resolved_text": user_text,
            "is_follow_up": True,
            "has_pronoun": has_pronoun,
            "context_description": None,
            "last_intent_tag": None,
        }

    resolved_text, context_desc = _rewrite_with_context(user_text, context)

    return {
        "original_text": user_text,
        "resolved_text": resolved_text,
        "is_follow_up": True,
        "has_pronoun": has_pronoun,
        "context_description": context_desc,
        "last_intent_tag": context["last_intent_tag"],
    }
