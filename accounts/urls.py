"""URLs pour l'app accounts."""

from django.urls import path

from . import views
from .admin_views import (
    role_list_view, role_create_view, role_edit_view, role_delete_view,
    user_list_view, user_assign_roles_view,
)

app_name = "accounts"

urlpatterns = [
    # Authentification
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Profil
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    # Mot de passe
    path("password/change/", views.password_change_view, name="password_change"),
    path("password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password/reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Sessions
    path("sessions/", views.sessions_view, name="sessions"),
    # Admin - Gestion des rôles
    path("admin/roles/", role_list_view, name="admin_role_list"),
    path("admin/roles/create/", role_create_view, name="admin_role_create"),
    path("admin/roles/<int:role_id>/edit/", role_edit_view, name="admin_role_edit"),
    path("admin/roles/<int:role_id>/delete/", role_delete_view, name="admin_role_delete"),
    path("admin/users/", user_list_view, name="admin_user_list"),
    path("admin/users/<uuid:user_id>/roles/", user_assign_roles_view, name="admin_user_assign_roles"),
    # Notifications
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/dropdown/", views.notification_dropdown, name="notification_dropdown"),
    path("notifications/<uuid:notification_id>/mark-read/", views.notification_mark_read, name="notification_mark_read"),
    path("notifications/mark-all-read/", views.notification_mark_all_read, name="notification_mark_all_read"),
    path("notifications/preferences/", views.notification_preferences, name="notification_preferences"),
    # Logs système (superuser uniquement)
    path("admin/logs/", views.logs_view, name="logs_view"),
]
