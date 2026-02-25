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

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID"
    )

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

    avatar = models.ImageField(
        "avatar", upload_to="avatars/%Y/%m/", blank=True, null=True
    )

    is_active = models.BooleanField(
        "actif",
        default=True,
        help_text="Désactivez cette case au lieu de supprimer le compte.",
    )

    is_staff = models.BooleanField(
        "statut staff",
        default=False,
        help_text="Détermine si l'utilisateur peut accéder à l'admin.",
    )

    is_verified = models.BooleanField(
        "vérifié", default=False, help_text="Email vérifié."
    )

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
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="utilisateur",
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
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
        verbose_name="utilisateur",
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
        User,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="utilisateur",
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
        status = "active" if self.is_active else "inactive"
        return f"Session de {self.user.email} ({status})"

    def deactivate(self):
        """Désactive la session."""
        self.is_active = False
        self.save(update_fields=["is_active"])


class PagePermission(models.Model):
    """Représente une page/vue de l'application pour la gestion des permissions."""

    HTTP_METHODS = [
        ("GET", "Voir"),
        ("POST", "Ajouter"),
        ("PUT", "Modifier"),
        ("DELETE", "Supprimer"),
        ("PATCH", "Modifier partiellement"),
    ]

    app_name = models.CharField("nom de l'app", max_length=100, db_index=True)
    view_name = models.CharField("nom de la vue", max_length=200)
    url_name = models.CharField("nom de l'URL", max_length=200, db_index=True)
    url_pattern = models.CharField("pattern d'URL", max_length=500)
    description = models.TextField("description", blank=True)
    codename = models.CharField(
        "code unique", max_length=300, unique=True, db_index=True
    )
    http_method = models.CharField(
        "méthode HTTP", max_length=10, choices=HTTP_METHODS, default="GET"
    )
    is_active = models.BooleanField("actif", default=True)
    auto_detected = models.BooleanField("détecté automatiquement", default=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        """Meta options pour le modèle PagePermission."""

        verbose_name = "permission de page"
        verbose_name_plural = "permissions de pages"
        ordering = ["app_name", "view_name", "http_method"]
        unique_together = ["app_name", "url_name", "http_method"]
        indexes = [
            models.Index(fields=["app_name", "is_active"]),
            models.Index(fields=["codename"]),
        ]

    def __str__(self):
        """Retourne la représentation string de la permission."""
        method = self.get_http_method_display()
        return f"{self.app_name} - {self.view_name} ({method})"

    def save(self, *args, **kwargs):
        """Sauvegarde la permission avec génération du codename."""
        if not self.codename:
            self.codename = (
                f"{self.app_name}_{self.url_name}_{self.http_method.lower()}"
            )
        super().save(*args, **kwargs)


class Role(models.Model):
    """Rôle personnalisé avec permissions de pages."""

    COLOR_CHOICES = [
        ("#EF4444", "Rouge"),
        ("#F97316", "Orange"),
        ("#F59E0B", "Jaune"),
        ("#84CC16", "Vert lime"),
        ("#10B981", "Vert"),
        ("#06B6D4", "Cyan"),
        ("#3B82F6", "Bleu"),
        ("#6366F1", "Indigo"),
        ("#8B5CF6", "Violet"),
        ("#D946EF", "Fuchsia"),
        ("#EC4899", "Rose"),
        ("#6B7280", "Gris"),
    ]

    name = models.CharField("nom", max_length=100, unique=True)
    description = models.TextField("description", blank=True)
    color = models.CharField(
        "couleur", max_length=7, choices=COLOR_CHOICES, default="#3B82F6"
    )
    is_default = models.BooleanField(
        "rôle par défaut",
        default=False,
        help_text="Attribut automatiquement aux nouveaux utilisateurs",
    )
    is_active = models.BooleanField("actif", default=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        """Meta options pour le modèle Role."""

        verbose_name = "rôle"
        verbose_name_plural = "rôles"
        ordering = ["name"]

    def __str__(self):
        """Retourne le nom du rôle."""
        return self.name

    def get_permissions_count(self):
        """Retourne le nombre de permissions actives du rôle."""
        return self.page_permissions.filter(can_access=True).count()


class RolePagePermission(models.Model):
    """Association entre un rôle et une permission de page."""

    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="page_permissions"
    )
    page_permission = models.ForeignKey(
        PagePermission, on_delete=models.CASCADE, related_name="role_permissions"
    )
    can_access = models.BooleanField("peut accéder", default=False)
    can_add = models.BooleanField("peut ajouter", default=False)
    can_change = models.BooleanField("peut modifier", default=False)
    can_delete = models.BooleanField("peut supprimer", default=False)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        """Meta options pour le modèle RolePagePermission."""

        verbose_name = "permission de rôle"
        verbose_name_plural = "permissions de rôles"
        unique_together = ["role", "page_permission"]
        ordering = ["page_permission__app_name", "page_permission__view_name"]

    def __str__(self):
        """Retourne la représentation de la permission de rôle."""
        return f"{self.role.name} - {self.page_permission}"


class UserRole(models.Model):
    """Association entre un utilisateur et un rôle."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="assigned_users"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
    )
    assigned_at = models.DateTimeField("attribué le", auto_now_add=True)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        """Meta options pour le modèle UserRole."""

        verbose_name = "rôle utilisateur"
        verbose_name_plural = "rôles utilisateurs"
        unique_together = ["user", "role"]
        ordering = ["-assigned_at"]

    def __str__(self):
        """Retourne la représentation du rôle utilisateur."""
        return f"{self.user.email} - {self.role.name}"


class PermissionHistory(models.Model):
    """Historique des modifications de permissions."""

    ACTION_CHOICES = [
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
        ("ASSIGN", "Attribution"),
        ("REVOKE", "Révocation"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="permission_history",
        verbose_name="utilisateur concerné",
    )
    action = models.CharField("action", max_length=10, choices=ACTION_CHOICES)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    page_permission = models.ForeignKey(
        PagePermission, on_delete=models.SET_NULL, null=True, blank=True
    )
    details = models.JSONField("détails", default=dict, blank=True)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_actions",
    )
    performed_at = models.DateTimeField("effectué le", auto_now_add=True)
    ip_address = models.GenericIPAddressField("adresse IP", null=True, blank=True)

    class Meta:
        """Meta options pour le modèle PermissionHistory."""

        verbose_name = "historique de permission"
        verbose_name_plural = "historiques de permissions"
        ordering = ["-performed_at"]
        indexes = [
            models.Index(fields=["user", "-performed_at"]),
            models.Index(fields=["action", "-performed_at"]),
        ]

    def __str__(self):
        """Retourne la représentation de l'historique."""
        action = self.get_action_display()
        return f"{action} - {self.user.email} - {self.performed_at}"


class Notification(models.Model):
    """Système de notifications pour les utilisateurs."""

    NOTIFICATION_TYPES = [
        ("video_refused", "Refus de tournage vidéo"),
        ("video_confirmed", "Confirmation de tournage vidéo"),
        ("event_created", "Nouvel événement créé"),
        ("event_updated", "Événement modifié"),
        ("event_deleted", "Événement supprimé"),
        ("event_commented", "Nouveau commentaire"),
        ("event_validated", "Événement validé"),
        ("event_rejected", "Événement rejeté"),
        ("video_request_sent", "Demande de tournage envoyée"),
        ("feedback_new_ticket", "Nouveau ticket de feedback"),
        ("feedback_status_changed", "Statut de ticket modifié"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="utilisateur",
    )

    notification_type = models.CharField(
        "type", max_length=50, choices=NOTIFICATION_TYPES
    )

    title = models.CharField("titre", max_length=200)

    message = models.TextField("message")

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="événement",
    )

    video_request = models.ForeignKey(
        "events.VideoRequestLog",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="demande vidéo",
    )

    is_read = models.BooleanField("lue", default=False)

    link = models.URLField("lien", blank=True)

    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        """Meta options pour le modèle Notification."""

        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["notification_type", "-created_at"]),
        ]

    def __str__(self):
        """Retourne la représentation de la notification."""
        date_str = self.created_at.strftime("%d/%m/%Y %H:%M")
        return f"{self.title} - {self.user.email} - {date_str}"

    def mark_as_read(self):
        """Marque la notification comme lue."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])

    @classmethod
    def get_unread_count(cls, user):
        """Retourne le nombre de notifications non lues."""
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def get_recent_for_user(cls, user, limit=5):
        """Retourne les notifications récentes d'un utilisateur."""
        return cls.objects.filter(user=user).order_by("-created_at")[:limit]


class UserNotificationPreference(models.Model):
    """Préférences de notification par utilisateur et par type."""

    # Types de notifications disponibles
    NOTIFICATION_TYPES = [
        ("video_refused", "Refus de tournage vidéo"),
        ("video_confirmed", "Confirmation de tournage vidéo"),
        ("event_created", "Nouvel événement créé"),
        ("event_updated", "Événement modifié"),
        ("event_deleted", "Événement supprimé"),
        ("event_commented", "Nouveau commentaire"),
        ("event_validated", "Événement validé"),
        ("event_rejected", "Événement rejeté"),
        ("video_request_sent", "Demande de tournage envoyée"),
        ("feedback_new_ticket", "Nouveau ticket de feedback"),
        ("feedback_status_changed", "Statut de ticket modifié"),
    ]

    # Types accessibles aux utilisateurs basiques
    BASIC_USER_TYPES = ["event_validated", "event_commented"]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name="utilisateur",
    )

    notification_type = models.CharField(
        "type de notification", max_length=50, choices=NOTIFICATION_TYPES
    )

    # Canal in-app
    in_app_enabled = models.BooleanField("notification in-app activée", default=True)

    # Canal email
    email_enabled = models.BooleanField("notification email activée", default=False)

    created_at = models.DateTimeField("créée le", auto_now_add=True)
    updated_at = models.DateTimeField("modifiée le", auto_now=True)

    class Meta:
        """Meta options pour le modèle UserNotificationPreference."""

        verbose_name = "préférence de notification"
        verbose_name_plural = "préférences de notifications"
        unique_together = ["user", "notification_type"]
        ordering = ["notification_type"]

    def __str__(self):
        """Retourne la représentation de la préférence."""
        notif_type = self.get_notification_type_display()
        return f"{self.user.email} - {notif_type}"

    @classmethod
    def get_user_preferences(cls, user):
        """Récupère ou crée les préférences pour un utilisateur."""
        # Vérifier si l'utilisateur a le rôle Communication
        is_comm = user.user_roles.filter(
            role__name="Communication", is_active=True
        ).exists()

        if is_comm:
            # Communication : toutes les notifications, configurables
            available_types = [t[0] for t in cls.NOTIFICATION_TYPES]
            default_enabled = True
        else:
            # Utilisateur basique : uniquement validation et commentaires
            available_types = cls.BASIC_USER_TYPES
            default_enabled = True

        preferences = {}
        for notif_type in available_types:
            pref, created = cls.objects.get_or_create(
                user=user,
                notification_type=notif_type,
                defaults={"in_app_enabled": default_enabled, "email_enabled": False},
            )
            preferences[notif_type] = pref

        return preferences

    @classmethod
    def is_notification_allowed(cls, user, notification_type, channel="in_app"):
        """Vérifie si une notification est autorisée pour l'utilisateur."""
        # Vérifier si l'utilisateur a activé les notifications globalement
        if hasattr(user, "profile") and not user.profile.notification_enabled:
            return False

        # Vérifier si le type est dans les types disponibles pour l'utilisateur
        is_comm = user.user_roles.filter(
            role__name="Communication", is_active=True
        ).exists()

        if not is_comm and notification_type not in cls.BASIC_USER_TYPES:
            return False

        # Récupérer la préférence
        try:
            pref = cls.objects.get(user=user, notification_type=notification_type)
            if channel == "in_app":
                return pref.in_app_enabled
            elif channel == "email":
                return pref.email_enabled
        except cls.DoesNotExist:
            # Par défaut, autorisé en in-app pour les types autorisés
            return channel == "in_app"

        return False
