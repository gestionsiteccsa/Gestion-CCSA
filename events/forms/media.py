"""Formulaires pour la gestion des médias (images et documents)."""

import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from events.models import EventDocument, EventImage


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
