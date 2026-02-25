"""URLs pour l'app feedback."""

from django.urls import path

from feedback import views

app_name = "feedback"

urlpatterns = [
    path("", views.FeedbackListView.as_view(), name="ticket_list"),
    path("create/", views.FeedbackCreateView.as_view(), name="ticket_create"),
    path("<int:pk>/", views.FeedbackDetailView.as_view(), name="ticket_detail"),
    path(
        "<int:pk>/update-status/",
        views.FeedbackUpdateStatusView.as_view(),
        name="ticket_update_status",
    ),
    path("admin/", views.FeedbackAdminListView.as_view(), name="admin_list"),
    path("settings/", views.FeedbackSettingsView.as_view(), name="settings"),
]
