import uuid
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="")
    color = models.CharField(max_length=7, default="#4F46E5")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Intent(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="intents"
    )
    description = models.TextField(blank=True, default="")
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "tag"]

    def __str__(self):
        return f"{self.category.name} > {self.tag}"


class Pattern(models.Model):
    intent = models.ForeignKey(
        Intent, on_delete=models.CASCADE, related_name="patterns"
    )
    text = models.CharField(max_length=500)
    is_regex = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["text"]

    def __str__(self):
        return f"[{self.intent.tag}] {self.text}"


class Response(models.Model):
    intent = models.ForeignKey(
        Intent, on_delete=models.CASCADE, related_name="responses"
    )
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.intent.tag}] {self.text[:60]}..."


class ChatSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.session_id}"

    def end_session(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    text = models.TextField()
    matched_intent = models.ForeignKey(
        Intent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_messages",
    )
    confidence_score = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"[{self.sender}] {self.text[:50]}..."


class FallbackLog(models.Model):
    DEPARTMENT_CHOICES = [
        ("general", "General"),
        ("admissions", "Admissions Office"),
        ("examcell", "Exam Cell"),
        ("accounts", "Accounts / Fees"),
        ("placement", "Placement Cell"),
        ("hostel", "Hostel Office"),
        ("hod_cse", "HOD - CSE"),
        ("hod_ece", "HOD - ECE"),
        ("hod_eee", "HOD - EEE"),
        ("hod_mech", "HOD - Mechanical"),
        ("hod_civil", "HOD - Civil"),
        ("principal", "Principal Office"),
    ]

    user_message = models.TextField()
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="fallbacks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    # Escalation fields
    assigned_department = models.CharField(
        max_length=50, choices=DEPARTMENT_CHOICES,
        blank=True, default=""
    )
    escalated_at = models.DateTimeField(null=True, blank=True)

    # Learning fields: admin provides an answer → auto-creates intent
    admin_response = models.TextField(blank=True, default="")
    learned_intent = models.ForeignKey(
        Intent, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="learned_from"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Unmatched: {self.user_message[:60]}..."
