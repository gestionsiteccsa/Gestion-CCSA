"""Models pour l'app url_shortener."""

import random
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.urls import reverse


class ShortenedURL(models.Model):
    """Modèle pour stocker les URLs raccourcies.

    Attributes:
        code: Code court unique pour l'URL (ex: "ErD99" ou "monlien")
        original_url: L'URL externe longue à raccourcir
        created_by: L'utilisateur qui a créé le lien
        created_at: Date de création
        updated_at: Date de dernière modification
    """

    # Génération d'un code aléatoire par défaut
    ALPHABET = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    CODE_LENGTH = 6

    code = models.CharField(
        "code court",
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Code unique pour l'URL courte (laissez vide pour génération automatique)",
    )

    original_url = models.URLField(
        "URL originale",
        max_length=2000,
        validators=[URLValidator()],
        help_text="L'URL externe à raccourcir",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shortened_urls",
        verbose_name="créé par",
    )

    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        verbose_name = "URL raccourcie"
        verbose_name_plural = "URLs raccourcies"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["created_by", "-created_at"]),
        ]

    def __str__(self):
        """Représentation string de l'URL raccourcie."""
        return f"{self.code} → {self.original_url[:50]}..."

    def clean(self):
        """Validation du modèle."""
        super().clean()

        # Vérifier que l'URL ne pointe pas vers l'intranet lui-même
        if self.original_url:
            from urllib.parse import urlparse

            parsed = urlparse(self.original_url)

            # Récupérer le domaine actuel
            current_domain = (
                getattr(settings, "ALLOWED_HOSTS", ["localhost"])[0]
                if settings.ALLOWED_HOSTS
                else "localhost"
            )

            # Vérifier si l'URL pointe vers le même domaine
            if parsed.netloc and current_domain in parsed.netloc:
                raise ValidationError(
                    {
                        "original_url": "Vous ne pouvez pas raccourcir une URL interne à l'intranet."
                    }
                )

        # Vérifier le code personnalisé
        if self.code:
            # Supprimer les espaces
            self.code = self.code.strip()

            # Vérifier les caractères autorisés (alphanumériques uniquement)
            if not self.code.replace("-", "").replace("_", "").isalnum():
                raise ValidationError(
                    {
                        "code": "Le code ne peut contenir que des lettres, chiffres, tirets (-) et underscores (_)."
                    }
                )

            # Vérifier la longueur minimale
            if len(self.code) < 3:
                raise ValidationError(
                    {"code": "Le code doit faire au moins 3 caractères."}
                )

    def save(self, *args, **kwargs):
        """Sauvegarde avec génération automatique du code si nécessaire."""
        # Si pas de code fourni, générer un code aléatoire
        if not self.code:
            self.code = self._generate_unique_code()

        self.clean()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        """Génère un code unique aléatoire."""
        max_attempts = 100
        for _ in range(max_attempts):
            code = "".join(random.choices(self.ALPHABET, k=self.CODE_LENGTH))
            if not ShortenedURL.objects.filter(code=code).exists():
                return code

        # Si on n'a pas trouvé de code unique après max_attempts essais
        raise Exception("Impossible de générer un code unique")

    def get_absolute_url(self):
        """Retourne l'URL de redirection."""
        return reverse("url_shortener:redirect", kwargs={"code": self.code})

    def get_short_url(self):
        """Retourne l'URL courte complète."""
        from django.contrib.sites.models import Site

        try:
            domain = Site.objects.get_current().domain
        except:
            domain = (
                getattr(settings, "ALLOWED_HOSTS", ["localhost"])[0]
                if settings.ALLOWED_HOSTS
                else "localhost"
            )

        protocol = "https" if not settings.DEBUG else "http"
        return f"{protocol}://{domain}/r/{self.code}"

    def delete_link(self):
        """Supprime le lien raccourci."""
        self.delete()
