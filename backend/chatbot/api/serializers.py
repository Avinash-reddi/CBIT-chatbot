from rest_framework import serializers
from chatbot.models import (
    Category, Intent, Pattern, Response,
    ChatSession, ChatMessage, FallbackLog,
)


class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ["id", "text", "is_regex", "created_at"]


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ["id", "text", "is_active", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    intent_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "icon",
            "color", "is_active", "intent_count", "created_at",
        ]

    def get_intent_count(self, obj):
        return obj.intents.filter(is_active=True).count()


class IntentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    pattern_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = Intent
        fields = [
            "id", "tag", "category", "category_name", "description",
            "priority", "is_active", "pattern_count", "response_count", "updated_at",
        ]

    def get_pattern_count(self, obj):
        return obj.patterns.count()

    def get_response_count(self, obj):
        return obj.responses.count()


class IntentDetailSerializer(serializers.ModelSerializer):
    patterns = PatternSerializer(many=True)
    responses = ResponseSerializer(many=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Intent
        fields = [
            "id", "tag", "category", "category_name", "description",
            "priority", "is_active", "patterns", "responses",
            "created_at", "updated_at",
        ]

    def create(self, validated_data):
        patterns_data = validated_data.pop("patterns")
        responses_data = validated_data.pop("responses")
        intent = Intent.objects.create(**validated_data)
        for p in patterns_data:
            Pattern.objects.create(intent=intent, **p)
        for r in responses_data:
            Response.objects.create(intent=intent, **r)
        return intent

    def update(self, instance, validated_data):
        patterns_data = validated_data.pop("patterns", None)
        responses_data = validated_data.pop("responses", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if patterns_data is not None:
            instance.patterns.all().delete()
            for p in patterns_data:
                Pattern.objects.create(intent=instance, **p)
        if responses_data is not None:
            instance.responses.all().delete()
            for r in responses_data:
                Response.objects.create(intent=instance, **r)
        return instance


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id", "sender", "text", "matched_intent",
            "confidence_score", "timestamp",
        ]


class ChatSessionListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "session_id", "started_at", "ended_at", "is_active",
            "message_count", "last_message", "user_ip",
        ]

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.text[:100] if last else None


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    session_id = serializers.UUIDField(required=False, allow_null=True)


class FallbackLogSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source="session.session_id", read_only=True)
    learned_intent_tag = serializers.CharField(
        source="learned_intent.tag", read_only=True, default=None
    )

    class Meta:
        model = FallbackLog
        fields = [
            "id", "user_message", "session_id", "created_at", "resolved",
            "assigned_department", "escalated_at", "admin_response",
            "learned_intent_tag", "resolved_at", "resolved_by",
        ]


class DashboardStatsSerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_intents = serializers.IntegerField()
    total_unanswered = serializers.IntegerField()
    messages_today = serializers.IntegerField()
    top_intents = serializers.ListField()
    category_distribution = serializers.ListField()
    daily_messages = serializers.ListField()
