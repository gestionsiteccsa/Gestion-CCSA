"""Formulaires pour l'app feedback."""

from django import forms

from feedback.models import FeedbackComment, FeedbackSettings, FeedbackTicket


class FeedbackTicketForm(forms.ModelForm):
    """Formulaire de création d'un ticket de feedback."""

    class Meta:  # noqa: D106
        """Meta options pour le formulaire."""

        model = FeedbackTicket
        fields = ["title", "description", "ticket_type", "priority", "screenshot"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Titre du ticket",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Décrivez le problème ou la suggestion...",
                    "rows": 6,
                }
            ),
            "ticket_type": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "screenshot": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/png, image/jpeg",
                }
            ),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "ticket_type": "Type",
            "priority": "Priorité",
            "screenshot": "Capture d'écran (optionnel)",
        }
        help_texts = {
            "screenshot": "Formats acceptés : JPG, PNG (max 2MB)",
        }

    def __init__(self, *args, **kwargs):
        """Initialize le formulaire avec le user."""
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_screenshot(self):
        """Validate la taille de l'image."""  # noqa: D401
        screenshot = self.cleaned_data.get("screenshot")
        if screenshot:
            # Limite à 2MB
            if screenshot.size > 2 * 1024 * 1024:
                raise forms.ValidationError(
                    "La taille de l'image ne doit pas dépasser 2MB."
                )
        return screenshot

    def save(self, commit=True):
        """Sauvegarde le ticket avec created_by."""
        ticket = super().save(commit=False)
        if self.user:
            ticket.created_by = self.user
        if commit:
            ticket.save()
        return ticket


class FeedbackCommentForm(forms.ModelForm):
    """Formulaire d'ajout d'un commentaire."""

    class Meta:  # noqa: D106
        """Meta options pour le formulaire de commentaire."""

        model = FeedbackComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ajouter un commentaire...",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "content": "Commentaire",
        }

    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec ticket et user."""
        self.ticket = kwargs.pop("ticket", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """Sauvegarde le commentaire avec ticket et author."""
        comment = super().save(commit=False)
        if self.ticket:
            comment.ticket = self.ticket
        if self.user:
            comment.author = self.user
            # Vérifier si l'utilisateur a le rôle Support
            if self.user.user_roles.filter(
                role__name="Support", is_active=True
            ).exists():
                comment.is_staff_response = True
        if commit:
            comment.save()
        return comment


class FeedbackSettingsForm(forms.ModelForm):
    """Formulaire de configuration des paramètres feedback."""

    class Meta:  # noqa: D106
        """Meta options pour le formulaire de paramètres."""

        model = FeedbackSettings
        fields = [
            "email_recipients",
            "notify_on_new_ticket",
            "notify_on_status_change",
            "from_email",
        ]
        widgets = {
            "email_recipients": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "size": "5",
                }
            ),
            "notify_on_new_ticket": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "notify_on_status_change": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "from_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "support@example.com",
                }
            ),
        }
        labels = {
            "email_recipients": "Destinataires des emails",
            "notify_on_new_ticket": "Notifier sur nouveau ticket",
            "notify_on_status_change": "Notifier sur changement de statut",
            "from_email": "Email d'expédition",
        }
        help_texts = {
            "email_recipients": "Sélectionnez les utilisateurs qui recevront les notifications",
            "from_email": (
                "Email utilisé pour envoyer les notifications"
                " (laissez vide pour utiliser l'email par défaut)"
            ),
        }
