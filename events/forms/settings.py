"""Formulaires pour la configuration des événements."""

from django import forms
from django.core.exceptions import ValidationError

from events.models import EventSettings, VideoNotificationSettings


class VideoNotificationSettingsForm(forms.ModelForm):
    """Formulaire de configuration de l'email de notification vidéo."""

    class Meta:
        model = VideoNotificationSettings
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm "
                        "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                        "transition-all duration-200 ease-in-out placeholder-slate-400 text-slate-900"
                    ),
                    "placeholder": "email@exemple.com",
                }
            ),
        }
        labels = {
            "email": "Email de notification",
        }
        help_texts = {
            "email": "Adresse email qui recevra les demandes de tournage vidéo",
        }

    def clean_email(self):
        """Valide que l'email n'est pas vide."""
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip()
            if not email:
                raise ValidationError("L'email ne peut pas être vide.")
        return email


class EventSettingsForm(forms.ModelForm):
    """Formulaire de configuration des paramètres globaux des événements.

    Accessible uniquement aux superadmins via l'interface d'administration.
    """

    class Meta:
        model = EventSettings
        fields = [
            "video_notification_email",
            "default_from_email",
            "max_events_per_user",
            "max_images_per_event",
            "auto_validate_events",
        ]
        widgets = {
            "video_notification_email": forms.EmailInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm "
                        "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                        "transition-all duration-200 ease-in-out placeholder-slate-400 text-slate-900"
                    ),
                    "placeholder": "email@exemple.com",
                }
            ),
            "default_from_email": forms.EmailInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm "
                        "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                        "transition-all duration-200 ease-in-out placeholder-slate-400 text-slate-900"
                    ),
                    "placeholder": "noreply@exemple.com",
                }
            ),
            "max_events_per_user": forms.NumberInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm "
                        "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                        "transition-all duration-200 ease-in-out text-slate-900"
                    ),
                    "min": 1,
                    "max": 1000,
                }
            ),
            "max_images_per_event": forms.NumberInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm "
                        "focus:ring-2 focus:ring-primary-500 focus:border-primary-500 "
                        "transition-all duration-200 ease-in-out text-slate-900"
                    ),
                    "min": 1,
                    "max": 50,
                }
            ),
            "auto_validate_events": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 text-primary-600 border-slate-300 rounded focus:ring-primary-500",
                }
            ),
        }
        labels = {
            "video_notification_email": "Email de notification vidéo",
            "default_from_email": "Email d'expédition",
            "max_events_per_user": "Nombre maximum d'événements par utilisateur",
            "max_images_per_event": "Nombre maximum d'images par événement",
            "auto_validate_events": "Validation automatique des événements",
        }
        help_texts = {
            "video_notification_email": "Adresse email qui recevra les demandes de tournage vidéo",
            "default_from_email": "Adresse email utilisée pour envoyer les notifications",
            "max_events_per_user": "Limite le nombre d'événements qu'un utilisateur peut créer",
            "max_images_per_event": "Limite le nombre d'images qu'un événement peut contenir",
            "auto_validate_events": "Si activé, les événements seront automatiquement validés",
        }

    def clean_video_notification_email(self):
        """Valide l'email de notification vidéo."""
        email = self.cleaned_data.get("video_notification_email")
        if email:
            email = email.strip()
            if not email:
                raise ValidationError("L'email de notification ne peut pas être vide.")
        return email

    def clean_default_from_email(self):
        """Valide l'email d'expédition."""
        email = self.cleaned_data.get("default_from_email")
        if email:
            email = email.strip()
            if not email:
                raise ValidationError("L'email d'expédition ne peut pas être vide.")
        return email
