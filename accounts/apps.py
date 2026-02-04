"""Configuration de l'app accounts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration de l'app accounts."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Comptes utilisateurs"

    def ready(self):
        """Import les signaux au démarrage de l'application."""
        # Import des signaux - nécessaire pour que Django les charge
        # Le import est fait ici pour éviter les imports circulaires
        # pylint: disable=import-outside-toplevel,unused-import
        import accounts.signals  # noqa
