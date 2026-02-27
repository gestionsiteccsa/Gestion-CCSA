"""Formulaire pour les commentaires sur les événements."""

from django import forms
from django.core.exceptions import ValidationError

from events.models import EventComment


class EventCommentForm(forms.ModelForm):
    """Formulaire de commentaire sur un événement."""

    class Meta:
        model = EventComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Votre commentaire...",
                }
            ),
        }
        labels = {
            "content": "Commentaire",
        }

    def clean_content(self):
        """Valide que le contenu n'est pas vide."""
        content = self.cleaned_data.get("content")
        if content:
            content = content.strip()
            if not content:
                raise ValidationError("Le commentaire ne peut pas être vide.")
        return content
