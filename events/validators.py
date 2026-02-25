"""Validateurs pour l'app events."""

import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageExtensionValidator:
    """Valide les extensions d'image autorisées."""

    def __init__(self, allowed_extensions=None):
        """Initialise le validateur avec les extensions autorisées."""
        if allowed_extensions is None:
            allowed_extensions = getattr(
                settings,
                "EVENTS_ALLOWED_EXTENSIONS",
                [".jpg", ".jpeg", ".png", ".webp"],
            )
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def __call__(self, value):
        """Valide l'extension du fichier."""
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Extension non autorisée. "
                f"Extensions autorisées: {', '.join(self.allowed_extensions)}"
            )

    def __eq__(self, other):
        """Compare deux validateurs."""
        return (
            isinstance(other, ImageExtensionValidator)
            and self.allowed_extensions == other.allowed_extensions
        )


@deconstructible
class ImageSizeValidator:
    """Valide la taille maximale d'une image."""

    def __init__(self, max_size_mb=None):
        """Initialise le validateur avec la taille max en Mo."""
        if max_size_mb is None:
            max_size_mb = getattr(settings, "EVENTS_MAX_IMAGE_SIZE_MB", 10)
        self.max_size = max_size_mb * 1024 * 1024  # Conversion en octets

    def __call__(self, value):
        """Valide la taille du fichier."""
        if value.size > self.max_size:
            max_size_mb = self.max_size // (1024 * 1024)
            raise ValidationError(f"La taille du fichier ne doit pas dépasser {max_size_mb} Mo.")

    def __eq__(self, other):
        """Compare deux validateurs."""
        return isinstance(other, ImageSizeValidator) and self.max_size == other.max_size
