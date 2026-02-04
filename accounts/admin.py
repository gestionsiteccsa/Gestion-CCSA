"""Configuration de l'admin pour l'app accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import LoginHistory, User, UserProfile, UserSession


class UserProfileInline(admin.StackedInline):
    """Inline pour le profil utilisateur."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profil"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuration de l'admin pour User."""

    inlines = (UserProfileInline,)

    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]

    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "phone_number", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
        (
            "Statut",
            {
                "fields": ("is_verified", "last_login", "date_joined"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ["last_login", "date_joined"]

    actions = ["activate_users", "deactivate_users"]

    @admin.action(description="Activer les utilisateurs sélectionnés")
    def activate_users(self, request, queryset):
        """Active les utilisateurs sélectionnés."""
        queryset.update(is_active=True)

    @admin.action(description="Désactiver les utilisateurs sélectionnés")
    def deactivate_users(self, request, queryset):
        """Désactive les utilisateurs sélectionnés."""
        queryset.update(is_active=False)


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour LoginHistory."""

    list_display = [
        "user",
        "timestamp",
        "ip_address",
        "success",
    ]

    list_filter = [
        "success",
        "timestamp",
    ]

    search_fields = ["user__email", "ip_address"]
    readonly_fields = ["user", "timestamp", "ip_address", "user_agent", "success", "failure_reason"]

    def has_add_permission(self, request):
        """Désactive l'ajout manuel d'historique."""
        return False

    def has_change_permission(self, request, obj=None):
        """Désactive la modification manuelle d'historique."""
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour UserSession."""

    list_display = [
        "user",
        "ip_address",
        "is_active",
        "created_at",
        "last_activity",
    ]

    list_filter = [
        "is_active",
        "created_at",
    ]

    search_fields = ["user__email", "ip_address", "session_key"]
    readonly_fields = [
        "user",
        "session_key",
        "ip_address",
        "user_agent",
        "created_at",
        "last_activity",
    ]

    def has_add_permission(self, request):
        """Désactive l'ajout manuel de session."""
        return False
