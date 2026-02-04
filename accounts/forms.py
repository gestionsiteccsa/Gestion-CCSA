"""Formulaires pour l'app accounts."""

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
)
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User, UserProfile


class UserRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription utilisateur."""

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        help_text="Votre mot de passe doit contenir au moins 8 caractères.",
    )

    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput,
        help_text="Entrez le même mot de passe pour vérification.",
    )

    accept_terms = forms.BooleanField(
        label="J'accepte les conditions d'utilisation",
        required=True,
        error_messages={"required": "Vous devez accepter les conditions pour continuer."},
    )

    class Meta:
        """Meta options pour UserRegistrationForm."""

        model = User
        fields = ["email", "first_name", "last_name"]
        labels = {
            "email": "Adresse email",
            "first_name": "Prénom",
            "last_name": "Nom",
        }

    def clean_email(self):
        """Vérifie que l'email est unique et valide."""
        email = self.cleaned_data.get("email")

        if not email:
            raise ValidationError("L'adresse email est obligatoire.")

        # Vérifier si la restriction de domaine est activée
        if getattr(settings, "ACCOUNTS_RESTRICT_EMAIL_DOMAIN", False):
            allowed_domain = getattr(settings, "ACCOUNTS_ALLOWED_EMAIL_DOMAIN", "")
            if allowed_domain and not email.lower().endswith(f"@{allowed_domain.lower()}"):
                raise ValidationError(
                    f"Les inscriptions sont limitées aux adresses email @{allowed_domain}."
                )

        # Vérifier l'unicité (insensible à la casse)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")

        return email

    def clean_password2(self):
        """Vérifie que les deux mots de passe correspondent."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les deux mots de passe ne correspondent pas.")

        return password2

    def save(self, commit=True):
        """Sauvegarde l'utilisateur avec le mot de passe."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserLoginForm(AuthenticationForm):
    """Formulaire de connexion."""

    username = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    remember_me = forms.BooleanField(label="Se souvenir de moi", required=False)


class UserUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur."""

    class Meta:
        """Meta options pour UserUpdateForm."""

        model = User
        fields = ["email", "first_name", "last_name", "phone_number", "avatar"]
        labels = {
            "email": "Adresse email",
            "first_name": "Prénom",
            "last_name": "Nom",
            "phone_number": "Numéro de téléphone",
            "avatar": "Photo de profil",
        }

    def clean_email(self):
        """Vérifie que le nouvel email n'est pas déjà utilisé."""
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")

        return email.lower()


class UserProfileForm(forms.ModelForm):
    """Formulaire du profil étendu."""

    class Meta:
        """Meta options pour UserProfileForm."""

        model = UserProfile
        fields = ["bio", "birth_date", "website", "location", "notification_enabled"]
        labels = {
            "bio": "Biographie",
            "birth_date": "Date de naissance",
            "website": "Site web",
            "location": "Localisation",
            "notification_enabled": "Activer les notifications",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }


class PasswordChangeForm(BasePasswordChangeForm):
    """Formulaire de changement de mot de passe."""

    old_password = forms.CharField(label="Ancien mot de passe", widget=forms.PasswordInput)

    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput,
        help_text="Votre mot de passe doit contenir au moins 8 caractères.",
    )

    new_password2 = forms.CharField(
        label="Confirmation du nouveau mot de passe", widget=forms.PasswordInput
    )
