"""
Fallback Learning Service.

When an admin provides an answer to an unanswered query, this service:
1. Finds or creates an appropriate intent
2. Adds the user's original question as a new pattern
3. Adds the admin's answer as a new response
4. Links the fallback to the learned intent
5. Future similar questions will be answered automatically
"""

import re
from django.utils import timezone
from django.utils.text import slugify
from chatbot.models import Category, Intent, Pattern, Response, FallbackLog


def _generate_intent_tag(user_message):
    """Generate a unique intent tag from the user message."""
    # Clean and truncate the message for a tag
    clean = re.sub(r"[^\w\s]", "", user_message.lower().strip())
    words = clean.split()[:4]  # Max 4 words
    base_tag = "_".join(words)
    tag = f"learned_{base_tag}"

    # Ensure uniqueness
    counter = 1
    final_tag = tag
    while Intent.objects.filter(tag=final_tag).exists():
        final_tag = f"{tag}_{counter}"
        counter += 1

    return final_tag


def _find_best_category(department):
    """Map department to the most appropriate category."""
    DEPT_CATEGORY_MAP = {
        "admissions": "admissions-courses",
        "examcell": "exams-schedules",
        "accounts": "fees-scholarships",
        "placement": "placements",
        "hostel": "campus-facilities",
        "hod_cse": "admissions-courses",
        "hod_ece": "admissions-courses",
        "hod_eee": "admissions-courses",
        "hod_mech": "admissions-courses",
        "hod_civil": "admissions-courses",
        "principal": "general",
        "general": "general",
    }

    slug = DEPT_CATEGORY_MAP.get(department, "general")
    try:
        return Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return Category.objects.first()


def learn_from_fallback(fallback_id, admin_response, category_id=None,
                         assigned_department="", resolved_by="admin"):
    """
    Create a new intent from an admin's answer to a fallback query.

    Args:
        fallback_id: ID of the FallbackLog entry
        admin_response: The answer text provided by admin
        category_id: Optional category ID (auto-detected if not provided)
        assigned_department: Department that handled this
        resolved_by: Username of the admin who resolved it

    Returns:
        dict with created intent info, or error details
    """
    try:
        fallback = FallbackLog.objects.get(id=fallback_id)
    except FallbackLog.DoesNotExist:
        return {"error": "Fallback not found"}

    if fallback.learned_intent:
        return {"error": "This fallback has already been learned"}

    # Determine category
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return {"error": "Category not found"}
    else:
        category = _find_best_category(assigned_department or "general")

    # Generate intent tag
    tag = _generate_intent_tag(fallback.user_message)

    # Check if a very similar pattern already exists
    existing_pattern = Pattern.objects.filter(
        text__iexact=fallback.user_message.strip()
    ).first()

    if existing_pattern:
        # Add the admin response to the existing intent instead
        intent = existing_pattern.intent
        Response.objects.create(intent=intent, text=admin_response)
    else:
        # Create new intent with pattern and response
        intent = Intent.objects.create(
            tag=tag,
            category=category,
            description=f"Auto-learned from fallback #{fallback_id}",
            priority=3,
            is_active=True,
        )
        Pattern.objects.create(intent=intent, text=fallback.user_message.strip())
        Response.objects.create(intent=intent, text=admin_response)

    # Mark the fallback as resolved and linked
    fallback.resolved = True
    fallback.admin_response = admin_response
    fallback.learned_intent = intent
    fallback.resolved_at = timezone.now()
    fallback.resolved_by = resolved_by
    if assigned_department:
        fallback.assigned_department = assigned_department
    fallback.save()

    # Clear intent cache so the new intent is immediately available
    from chatbot.services.intent_matcher import IntentMatcher
    IntentMatcher.clear_cache()

    return {
        "success": True,
        "intent_id": intent.id,
        "intent_tag": intent.tag,
        "is_new_intent": not bool(existing_pattern),
    }


def escalate_fallback(fallback_id, department, escalated_by="admin"):
    """
    Escalate a fallback query to a specific department.

    Args:
        fallback_id: ID of the FallbackLog entry
        department: Department code (from DEPARTMENT_CHOICES)
        escalated_by: Username of admin who escalated

    Returns:
        dict with escalation status
    """
    try:
        fallback = FallbackLog.objects.get(id=fallback_id)
    except FallbackLog.DoesNotExist:
        return {"error": "Fallback not found"}

    fallback.assigned_department = department
    fallback.escalated_at = timezone.now()
    fallback.save()

    return {
        "success": True,
        "department": department,
        "fallback_id": fallback_id,
    }


def get_learning_stats():
    """Get statistics about the learning system."""
    total_fallbacks = FallbackLog.objects.count()
    resolved = FallbackLog.objects.filter(resolved=True).count()
    learned = FallbackLog.objects.filter(learned_intent__isnull=False).count()
    escalated = FallbackLog.objects.filter(
        assigned_department__gt=""
    ).exclude(assigned_department="").count()
    pending = FallbackLog.objects.filter(resolved=False).count()

    return {
        "total_fallbacks": total_fallbacks,
        "resolved": resolved,
        "learned": learned,
        "escalated": escalated,
        "pending": pending,
        "learning_rate": round(learned / total_fallbacks * 100, 1) if total_fallbacks else 0,
    }
