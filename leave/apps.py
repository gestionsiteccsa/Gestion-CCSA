"""App de gestion des congés."""

from django.apps import AppConfig


class LeaveConfig(AppConfig):
    """Configuration de l'app leave."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "leave"
    verbose_name = "Gestion des Congés"

    def ready(self):
        """Import des signaux."""
        import leave.signals  # noqa: F401
