"""Modèles pour l'app pointage."""

from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class SectionTypeQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les types de sections."""

    def active(self):
        """Retourne uniquement les sections actives."""
        return self.filter(is_active=True)


class SectionType(models.Model):
    """Type de section pour le pointage (ex: Accueil, Appels, etc.)."""

    name = models.CharField(
        max_length=100,
        verbose_name="Nom",
        help_text="Nom de la section",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description optionnelle de la section",
    )
    color = models.CharField(
        max_length=7,
        default="#64748b",
        verbose_name="Couleur",
        help_text="Code couleur HEX (ex: #3b82f6)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Désactiver pour masquer la section",
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Ordre",
        help_text="Ordre d'affichage",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SectionTypeQuerySet.as_manager()

    class Meta:
        verbose_name = "Type de section"
        verbose_name_plural = "Types de section"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class DailyTrackingQuerySet(models.QuerySet):
    """QuerySet personnalisé pour les pointages journaliers."""

    def for_date(self, target_date):
        """Filtre les pointages pour une date spécifique."""
        return self.filter(date=target_date)

    def for_date_range(self, start_date, end_date):
        """Filtre les pointages pour une plage de dates."""
        return self.filter(date__range=[start_date, end_date])

    def with_sections(self):
        """Précharge les sections pour optimiser les requêtes."""
        return self.select_related("section", "created_by", "updated_by")

    def get_stats_for_date_range(self, start_date, end_date):
        """Récupère les statistiques agrégées par date.

        Args:
            start_date: Date de début
            end_date: Date de fin

        Returns:
            Liste de dictionnaires avec date et total_count
        """
        return (
            self.filter(date__range=[start_date, end_date])
            .values("date")
            .annotate(total_count=Sum("count"))
            .order_by("date")
        )


class DailyTrackingManager(models.Manager):
    """Manager personnalisé pour les pointages journaliers."""

    def get_queryset(self):
        return DailyTrackingQuerySet(self.model, using=self._db)

    def get_or_create_tracking(self, date, section, defaults=None):
        """Récupère ou crée un pointage pour une date et section données.

        Args:
            date: Date du pointage
            section: Instance de SectionType
            defaults: Dictionnaire de valeurs par défaut

        Returns:
            Tuple (instance, created)
        """
        defaults = defaults or {}
        return self.get_or_create(
            date=date,
            section=section,
            defaults=defaults,
        )


class DailyTracking(models.Model):
    """Pointage journalier pour une section."""

    date = models.DateField(
        verbose_name="Date",
        help_text="Date du pointage",
    )
    section = models.ForeignKey(
        SectionType,
        on_delete=models.CASCADE,
        verbose_name="Section",
        related_name="trackings",
    )
    count = models.PositiveIntegerField(
        default=0,
        verbose_name="Compteur",
        help_text="Nombre de visites/appels",
        validators=[MinValueValidator(0)],
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_trackings",
        verbose_name="Créé par",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_trackings",
        verbose_name="Modifié par",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DailyTrackingManager()

    class Meta:
        verbose_name = "Pointage journalier"
        verbose_name_plural = "Pointages journaliers"
        ordering = ["-date", "section__order"]
        unique_together = ["date", "section"]
        indexes = [
            models.Index(fields=["date", "section"]),
            models.Index(fields=["date"]),
            models.Index(fields=["section"]),
        ]

    def __str__(self):
        return f"{self.section.name} - {self.date} : {self.count}"

    def clean(self):
        """Validation du modèle."""
        if self.count < 0:
            raise ValidationError("Le compteur ne peut pas être négatif.")

    def save(self, *args, **kwargs):
        """Sauvegarde avec validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def update_count(self, delta, user):
        """Met à jour le compteur et crée une entrée d'historique.

        Args:
            delta: Valeur à ajouter (peut être négative)
            user: Utilisateur effectuant la modification

        Returns:
            bool: True si la mise à jour a réussi
        """
        previous_count = self.count
        new_count = previous_count + delta

        if new_count < 0:
            return False

        self.count = new_count
        self.updated_by = user
        self.save(update_fields=["count", "updated_by", "updated_at"])

        # Créer l'entrée d'historique
        TrackingHistory.objects.create(
            tracking=self,
            previous_count=previous_count,
            new_count=new_count,
            modified_by=user,
        )

        return True


class TrackingHistory(models.Model):
    """Historique des modifications de pointage."""

    tracking = models.ForeignKey(
        DailyTracking,
        on_delete=models.CASCADE,
        verbose_name="Pointage",
        related_name="history",
    )
    previous_count = models.IntegerField(
        verbose_name="Ancien compteur",
        help_text="Valeur avant modification",
    )
    new_count = models.IntegerField(
        verbose_name="Nouveau compteur",
        help_text="Valeur après modification",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modifié par",
    )
    modified_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de modification",
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Raison",
        help_text="Raison de la modification (optionnel)",
    )

    class Meta:
        verbose_name = "Historique de modification"
        verbose_name_plural = "Historiques de modifications"
        ordering = ["-modified_at"]

    def __str__(self):
        return f"{self.tracking.section.name} - {self.tracking.date} : {self.previous_count} → {self.new_count}"
