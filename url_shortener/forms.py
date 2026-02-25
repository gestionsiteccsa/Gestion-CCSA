"""Forms pour l'app url_shortener."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ShortenedURL


class ShortenedURLForm(forms.ModelForm):
    """Formulaire de création d'une URL raccourcie."""

    code = forms.CharField(
        label="Code personnalisé (optionnel)",
        max_length=20,
        required=False,
        help_text="Laissez vide pour générer un code aléatoire automatiquement (6 caractères). "
        "Minimum 3 caractères. Caractères autorisés : lettres, chiffres, tirets (-) et underscores (_).",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all",
                "placeholder": "Ex: monlien, ErD99, promo2024...",
            }
        ),
    )

    original_url = forms.URLField(
        label="URL à raccourcir",
        max_length=2000,
        widget=forms.URLInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all",
                "placeholder": "https://exemple.com/page-tres-longue-avec-beaucoup-de-texte",
            }
        ),
        help_text="Entrez l'URL externe que vous souhaitez raccourcir.",
    )

    class Meta:
        model = ShortenedURL
        fields = ["original_url", "code"]

    def clean_code(self):
        """Vérifie que le code n'existe pas déjà."""
        code = self.cleaned_data.get("code")

        if not code:
            return code

        # Nettoyer le code
        code = code.strip()

        # Vérifier les caractères autorisés
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed_chars for c in code):
            raise ValidationError(
                "Le code ne peut contenir que des lettres, chiffres, tirets (-) et underscores (_)."
            )

        # Vérifier la longueur minimale
        if len(code) < 3:
            raise ValidationError("Le code doit faire au moins 3 caractères.")

        # Vérifier l'unicité (sauf si c'est le même objet en édition)
        existing = ShortenedURL.objects.filter(code__iexact=code)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError(
                f"Le code '{code}' est déjà utilisé. Veuillez en choisir un autre."
            )

        return code

    def clean_original_url(self):
        """Vérifie l'URL originale."""
        url = self.cleaned_data.get("original_url")

        if url:
            # Vérifier que l'URL commence par http:// ou https://
            if not url.startswith(("http://", "https://")):
                raise ValidationError("L'URL doit commencer par http:// ou https://")

        return url

    def save(self, commit=True, user=None):
        """Sauvegarde avec l'utilisateur courant."""
        instance = super().save(commit=False)

        if user:
            instance.created_by = user

        if commit:
            instance.save()

        return instance
