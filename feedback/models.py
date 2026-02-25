"""Modèles pour l'app feedback."""

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class FeedbackTicket(models.Model):
    """Représente un ticket de feedback/bug report."""

    TICKET_TYPE_CHOICES = [
        ("bug", "Bug"),
        ("feature", "Amélioration"),
        ("question", "Question"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Faible"),
        ("medium", "Moyenne"),
        ("high", "Haute"),
        ("critical", "Critique"),
    ]

    STATUS_CHOICES = [
        ("new", "Nouveau"),
        ("in_progress", "En cours"),
        ("resolved", "Résolu"),
        ("closed", "Fermé"),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")

    description = models.TextField(verbose_name="Description")

    ticket_type = models.CharField(
        max_length=20, choices=TICKET_TYPE_CHOICES, default="bug", verbose_name="Type"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Priorité",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Statut",
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tickets",
        verbose_name="Créé par",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name="Assigné à",
    )

    screenshot = models.ImageField(
        upload_to="feedback/",
        blank=True,
        null=True,
        verbose_name="Capture d'écran",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        help_text="Formats acceptés : JPG, PNG (max 2MB)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Créé le", db_index=True
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:  # noqa: D106
        """Meta options pour le modèle FeedbackTicket."""

        verbose_name = "Ticket de feedback"
        verbose_name_plural = "Tickets de feedback"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["created_by", "-created_at"]),
        ]

    def __str__(self):  # noqa: D105
        return f"#{self.id} - {self.title}"

    def save(self, *args, **kwargs):
        """Sauvegarder avec validation de la taille de l'image."""
        if self.screenshot:
            # Limite à 2MB
            if self.screenshot.size > 2 * 1024 * 1024:
                from django.core.exceptions import ValidationError

                raise ValidationError("La taille de l'image ne doit pas dépasser 2MB.")
        super().save(*args, **kwargs)


class FeedbackComment(models.Model):
    """Représente un commentaire sur un ticket."""

    ticket = models.ForeignKey(
        FeedbackTicket,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Ticket",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_comments",
        verbose_name="Auteur",
    )

    content = models.TextField(verbose_name="Contenu")

    is_staff_response = models.BooleanField(
        default=False, verbose_name="Réponse du support"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:  # noqa: D106
        """Meta options pour le modèle FeedbackComment."""

        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["created_at"]

    def __str__(self):  # noqa: D105
        return f"Commentaire de {self.author.email} sur #{self.ticket.id}"


class FeedbackSettings(models.Model):
    """Paramètres globaux du système de feedback (Singleton)."""

    email_recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="feedback_email_notifications",
        verbose_name="Destinataires des emails",
    )

    notify_on_new_ticket = models.BooleanField(
        default=True, verbose_name="Notifier sur nouveau ticket"
    )

    notify_on_status_change = models.BooleanField(
        default=True, verbose_name="Notifier sur changement de statut"
    )

    from_email = models.EmailField(
        blank=True,
        verbose_name="Email d'expédition",
        help_text="Email utilisé pour envoyer les notifications",
    )

    class Meta:  # noqa: D106
        """Meta options pour le modèle FeedbackSettings."""

        verbose_name = "Paramètres de feedback"
        verbose_name_plural = "Paramètres de feedback"

    def __str__(self):  # noqa: D105
        return "Paramètres du feedback"

    def save(self, *args, **kwargs):
        """Empêcher la création de plusieurs instances (Singleton)."""
        if not self.pk and FeedbackSettings.objects.exists():
            # Met à jour l'instance existante
            existing = FeedbackSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Récupère ou crée les paramètres (Singleton)."""
        settings_obj, created = cls.objects.get_or_create(pk=1)
        return settings_obj
