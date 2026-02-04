"""Models pour l'app accounts."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager, UserSessionManager


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé.

    Utilise email comme identifiant principal au lieu de username.
    Le premier utilisateur créé devient automatiquement superutilisateur.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")

    email = models.EmailField(
        "adresse email",
        unique=True,
        error_messages={
            "unique": "Un utilisateur avec cet email existe déjà.",
        },
    )

    first_name = models.CharField("prénom", max_length=150, blank=True)

    last_name = models.CharField("nom", max_length=150, blank=True)

    phone_regex = RegexValidator(
        regex=(
            r"^(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9]"
            r"(?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})$"
        ),
        message="Le numéro de téléphone doit être au format français.",
    )
    phone_number = models.CharField(
        "numéro de téléphone", validators=[phone_regex], max_length=17, blank=True
    )

    avatar = models.ImageField("avatar", upload_to="avatars/%Y/%m/", blank=True, null=True)

    is_active = models.BooleanField(
        "actif", default=True, help_text="Désactivez cette case au lieu de supprimer le compte."
    )

    is_staff = models.BooleanField(
        "statut staff",
        default=False,
        help_text="Détermine si l'utilisateur peut accéder à l'admin.",
    )

    is_verified = models.BooleanField("vérifié", default=False, help_text="Email vérifié.")

    date_joined = models.DateTimeField("date d'inscription", default=timezone.now)

    last_login = models.DateTimeField("dernière connexion", blank=True, null=True)

    # Configuration
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        """Meta options pour le modèle User."""

        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active", "date_joined"]),
        ]

    def __str__(self):
        """Représentation string de l'utilisateur."""
        return self.email

    def get_full_name(self):
        """Retourne le nom complet."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Retourne le prénom."""
        return self.first_name

    def activate(self):
        """Active le compte utilisateur."""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def deactivate(self):
        """Désactive le compte utilisateur."""
        self.is_active = False
        self.save(update_fields=["is_active"])


class UserProfile(models.Model):
    """Profil étendu de l'utilisateur.

    One-to-One avec User pour stocker des informations supplémentaires.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="utilisateur"
    )

    bio = models.TextField("biographie", max_length=500, blank=True)

    birth_date = models.DateField("date de naissance", blank=True, null=True)

    website = models.URLField("site web", blank=True)

    location = models.CharField("localisation", max_length=100, blank=True)

    notification_enabled = models.BooleanField("notifications activées", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options pour le modèle UserProfile."""

        verbose_name = "profil utilisateur"
        verbose_name_plural = "profils utilisateurs"

    def __str__(self):
        """Retourne la représentation string du profil."""
        return f"Profil de {self.user.email}"


class LoginHistory(models.Model):
    """Historique des connexions des utilisateurs."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_history", verbose_name="utilisateur"
    )

    timestamp = models.DateTimeField("date et heure", auto_now_add=True)

    ip_address = models.GenericIPAddressField("adresse IP", null=True, blank=True)

    user_agent = models.TextField("user agent", blank=True)

    success = models.BooleanField("succès", default=True)

    failure_reason = models.CharField("raison de l'échec", max_length=100, blank=True)

    class Meta:
        """Meta options pour le modèle LoginHistory."""

        verbose_name = "historique de connexion"
        verbose_name_plural = "historiques de connexion"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
        ]

    def __str__(self):
        """Retourne la représentation string de l'historique."""
        status = "réussie" if self.success else "échouée"
        return f"Connexion {status} de {self.user.email} le {self.timestamp}"


class UserSession(models.Model):
    """Sessions actives des utilisateurs."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sessions", verbose_name="utilisateur"
    )

    session_key = models.CharField("clé de session", max_length=40, unique=True)

    ip_address = models.GenericIPAddressField("adresse IP", null=True, blank=True)

    user_agent = models.TextField("user agent", blank=True)

    is_active = models.BooleanField("active", default=True)

    created_at = models.DateTimeField("créée le", auto_now_add=True)

    last_activity = models.DateTimeField("dernière activité", auto_now=True)

    # Manager personnalisé
    objects = UserSessionManager()

    class Meta:
        """Meta options pour le modèle UserSession."""

        verbose_name = "session utilisateur"
        verbose_name_plural = "sessions utilisateurs"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["user", "-last_activity"]),
            models.Index(fields=["session_key"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        """Retourne la représentation string de la session."""
        return f"Session de {self.user.email} ({'active' if self.is_active else 'inactive'})"

    def deactivate(self):
        """Désactive la session."""
        self.is_active = False
        self.save(update_fields=["is_active"])
