"""Configuration de l'app feedback."""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """Configuration de l'application feedback."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "feedback"
    verbose_name = "Feedback"
