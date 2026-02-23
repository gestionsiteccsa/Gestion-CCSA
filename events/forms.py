"""Formulaires pour l'app events."""

import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from events.models import (Event, EventComment, EventDocument, EventImage,
                           EventRecurrence, EventSettings, Sector,
                           VideoNotificationSettings)
from events.widgets import ColoredCheckboxSelectMultiple


class EventForm(forms.ModelForm):
    """Formulaire de création/édition d'un événement."""

    sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.filter(is_active=True),
        widget=ColoredCheckboxSelectMultiple,
        label="Secteurs",
        required=True,
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "city",
            "start_datetime",
            "end_datetime",
            "sectors",
            "comm_before",
            "comm_during",
            "comm_after",
            "needs_filming",
            "needs_poster",
            "notify_on_publish",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre de l'événement"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Description détaillée de l'événement",
                }
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Salle polyvalente"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Saint-Quentin"}
            ),
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "comm_before": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comm_during": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comm_after": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "needs_filming": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "needs_poster": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notify_on_publish": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "location": "Lieu",
            "city": "Ville",
            "start_datetime": "Date et heure de début",
            "end_datetime": "Date et heure de fin",
            "sectors": "Secteurs",
            "comm_before": "Communication avant l'événement",
            "comm_during": "Communication pendant l'événement",
            "comm_after": "Communication après l'événement",
            "needs_filming": "Intervention pour filmer",
            "needs_poster": "Demande d'affiche",
            "notify_on_publish": "Recevoir un email lors de la confirmation de la publication",
        }

    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec uniquement les secteurs actifs."""
        super().__init__(*args, **kwargs)
        # Le queryset est déjà défini dans la déclaration du champ
        # mais on le met à jour ici pour être sûr d'avoir les données fraîches
        self.fields["sectors"].queryset = Sector.objects.filter(is_active=True)

        # Rendre les champs datetime cachés dans le template
        self.fields["start_datetime"].widget = forms.HiddenInput()
        self.fields["end_datetime"].widget = forms.HiddenInput()

    def clean(self):
        """Valide que la date de fin est postérieure à la date de début."""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

        # Vérifier que l'événement n'est pas dans le passé
        if start_datetime and start_datetime < timezone.now():
            raise ValidationError("La date de début ne peut pas être dans le passé.")

        return cleaned_data


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


class EventImageForm(forms.ModelForm):
    """Formulaire d'upload d'image pour un événement."""

    class Meta:
        model = EventImage
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
        }
        labels = {
            "image": "Image",
        }

    def __init__(self, *args, event=None, **kwargs):
        """Initialise le formulaire avec l'événement associé."""
        self.event = event
        super().__init__(*args, **kwargs)

    def clean_image(self):
        """Valide l'image uploadée."""
        image = self.cleaned_data.get("image")

        if image:
            # Vérifier l'extension
            ext = os.path.splitext(image.name)[1].lower()
            allowed_extensions = getattr(
                settings,
                "EVENTS_ALLOWED_EXTENSIONS",
                [".jpg", ".jpeg", ".png", ".webp"],
            )
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"Extension non autorisée. "
                    f"Extensions autorisées: {', '.join(allowed_extensions)}"
                )

            # Vérifier la taille
            max_size_mb = getattr(settings, "EVENTS_MAX_IMAGE_SIZE_MB", 10)
            max_size = max_size_mb * 1024 * 1024
            if image.size > max_size:
                raise ValidationError(
                    f"La taille du fichier ne doit pas dépasser {max_size_mb} Mo."
                )

            # Vérifier le nombre maximum d'images
            if self.event:
                max_images = getattr(settings, "EVENTS_MAX_IMAGES", 10)
                current_count = EventImage.objects.filter(event=self.event).count()
                if current_count >= max_images:
                    raise ValidationError(
                        f"Un événement ne peut pas avoir plus de {max_images} images."
                    )

        return image


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


class EventDocumentForm(forms.ModelForm):
    """Formulaire d'upload de document pour un événement."""

    class Meta:
        model = EventDocument
        fields = ["title", "description", "document"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Titre du document",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Description (optionnelle)",
                }
            ),
            "document": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.xls,.xlsx",
                }
            ),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "document": "Document",
        }

    def clean_document(self):
        """Valide le document uploadé."""
        document = self.cleaned_data.get("document")

        if document:
            ext = os.path.splitext(document.name)[1].lower()
            allowed_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"Extension non autorisée. "
                    f"Extensions autorisées: {', '.join(allowed_extensions)}"
                )

            # Vérifier la taille (max 20 Mo)
            max_size = 20 * 1024 * 1024
            if document.size > max_size:
                raise ValidationError(
                    "La taille du fichier ne doit pas dépasser 20 Mo."
                )

        return document


class EventRecurrenceForm(forms.ModelForm):
    """Formulaire de configuration de la récurrence d'un événement."""

    class Meta:
        model = EventRecurrence
        fields = [
            "recurrence_type",
            "interval",
            "end_date",
            "days_of_week",
            "day_of_month",
            "month_of_year",
            "max_occurrences",
        ]
        widgets = {
            "recurrence_type": forms.Select(attrs={"class": "form-control"}),
            "interval": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 365,
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "days_of_week": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: 0,2,4 pour Lun,Mer,Ven",
                }
            ),
            "day_of_month": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 31,
                }
            ),
            "month_of_year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 12,
                }
            ),
            "max_occurrences": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 100,
                }
            ),
        }
        labels = {
            "recurrence_type": "Type de récurrence",
            "interval": "Intervalle",
            "end_date": "Date de fin",
            "days_of_week": "Jours de la semaine",
            "day_of_month": "Jour du mois",
            "month_of_year": "Mois de l'année",
            "max_occurrences": "Nombre max d'occurrences",
        }
        help_texts = {
            "days_of_week": "Pour hebdomadaire: 0=Lundi, 1=Mardi, etc. Ex: 0,2,4",
            "day_of_month": "Pour mensuel: jour du mois (1-31)",
            "month_of_year": "Pour annuel: mois (1-12)",
        }

    def clean_days_of_week(self):
        """Valide le format des jours de la semaine."""
        days = self.cleaned_data.get("days_of_week")
        if days:
            try:
                day_list = [int(d.strip()) for d in days.split(",")]
                if not all(0 <= d <= 6 for d in day_list):
                    raise ValidationError(
                        "Les jours doivent être entre 0 (Lundi) et 6 (Dimanche)."
                    )
                return ",".join(str(d) for d in day_list)
            except ValueError:
                raise ValidationError(
                    "Format invalide. Utilisez des chiffres séparés par des virgules."
                )
        return days

    def clean(self):
        """Valide la cohérence des données."""
        cleaned_data = super().clean()
        recurrence_type = cleaned_data.get("recurrence_type")
        days_of_week = cleaned_data.get("days_of_week")
        day_of_month = cleaned_data.get("day_of_month")
        month_of_year = cleaned_data.get("month_of_year")

        if recurrence_type == "weekly" and not days_of_week:
            self.add_error(
                "days_of_week", "Veuillez spécifier au moins un jour de la semaine."
            )

        if recurrence_type == "monthly" and not day_of_month:
            self.add_error("day_of_month", "Veuillez spécifier le jour du mois.")

        if recurrence_type == "yearly" and not month_of_year:
            self.add_error("month_of_year", "Veuillez spécifier le mois de l'année.")

        return cleaned_data
