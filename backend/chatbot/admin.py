from django.contrib import admin
from .models import Category, Intent, Pattern, Response, ChatSession, ChatMessage, FallbackLog


class PatternInline(admin.TabularInline):
    model = Pattern
    extra = 1


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ["tag", "category", "priority", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["tag", "description"]
    inlines = [PatternInline, ResponseInline]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["session_id", "started_at", "is_active", "user_ip"]
    list_filter = ["is_active"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["session", "sender", "text_preview", "matched_intent", "timestamp"]
    list_filter = ["sender"]

    def text_preview(self, obj):
        return obj.text[:80]


@admin.register(FallbackLog)
class FallbackLogAdmin(admin.ModelAdmin):
    list_display = ["user_message_preview", "session", "created_at", "resolved"]
    list_filter = ["resolved"]

    def user_message_preview(self, obj):
        return obj.user_message[:80]
