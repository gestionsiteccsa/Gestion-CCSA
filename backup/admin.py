"""Admin pour les modèles de sauvegarde."""

from django.contrib import admin

from backup.models import BackupConfiguration, BackupHistory


@admin.register(BackupConfiguration)
class BackupConfigurationAdmin(admin.ModelAdmin):
    """Admin pour la configuration des sauvegardes."""

    list_display = [
        "name",
        "backup_type",
        "frequency",
        "is_active",
        "keep_last_n",
        "updated_at",
    ]
    list_filter = ["is_active", "backup_type", "frequency"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Général", {"fields": ("name", "is_active")}),
        (
            "Paramètres de sauvegarde",
            {"fields": ("backup_type", "frequency", "keep_last_n")},
        ),
        ("Stockage", {"fields": ("backup_directory",)}),
        (
            "Métadonnées",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(BackupHistory)
class BackupHistoryAdmin(admin.ModelAdmin):
    """Admin pour l'historique des sauvegardes."""

    list_display = [
        "started_at",
        "backup_type",
        "trigger",
        "status",
        "get_file_size_display",
        "get_duration",
        "created_by",
    ]
    list_filter = ["status", "backup_type", "trigger"]
    readonly_fields = [
        "started_at",
        "completed_at",
        "file_size",
        "get_file_size_display",
        "get_duration",
    ]
    search_fields = ["file_path", "error_message"]
    date_hierarchy = "started_at"

    fieldsets = (
        (
            "Informations générales",
            {"fields": ("backup_type", "trigger", "status", "created_by")},
        ),
        ("Fichier", {"fields": ("file_path", "file_size", "get_file_size_display")}),
        ("Timing", {"fields": ("started_at", "completed_at", "get_duration")}),
        ("Erreur", {"fields": ("error_message",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        """Désactive l'ajout manuel d'entrées d'historique."""
        return False

    def has_change_permission(self, request, obj=None):
        """Désactive la modification des entrées d'historique."""
        return False
