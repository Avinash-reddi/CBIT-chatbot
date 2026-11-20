from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"admin/categories", views.CategoryViewSet)
router.register(r"admin/intents", views.IntentViewSet)
router.register(r"admin/patterns", views.PatternViewSet)
router.register(r"admin/responses", views.ResponseViewSet)

urlpatterns = [
    # Public chat endpoints
    path("chat/", views.chat_message, name="chat-message"),
    path("chat/session/", views.create_session, name="create-session"),
    path("chat/session/<uuid:session_id>/history/", views.session_history, name="session-history"),
    path("categories/public/", views.public_categories, name="public-categories"),

    # Admin analytics
    path("admin/dashboard/stats/", views.dashboard_stats, name="dashboard-stats"),
    path("admin/chat-history/", views.admin_chat_history, name="admin-chat-history"),
    path("admin/chat-history/<uuid:session_id>/", views.admin_session_detail, name="admin-session-detail"),
    path("admin/fallbacks/", views.admin_fallbacks, name="admin-fallbacks"),
    path("admin/fallbacks/<int:pk>/resolve/", views.resolve_fallback, name="resolve-fallback"),
    path("admin/fallbacks/<int:pk>/answer/", views.answer_fallback, name="answer-fallback"),
    path("admin/fallbacks/<int:pk>/escalate/", views.escalate_fallback_view, name="escalate-fallback"),
    path("admin/departments/", views.department_list, name="department-list"),

    # Router URLs (CRUD ViewSets)
    path("", include(router.urls)),
]
