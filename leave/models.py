"""Modèles pour la gestion des congés."""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from events.models import Sector

User = get_user_model()


class FrenchHoliday(models.Model):
    """Jours fériés français."""

    date = models.DateField(unique=True, verbose_name="Date")
    name = models.CharField(max_length=100, verbose_name="Nom")
    year = models.IntegerField(verbose_name="Année")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Jour férié"
        verbose_name_plural = "Jours fériés"
        ordering = ["date"]

    def __str__(self):
        return f"{self.name} ({self.date})"


class LeaveCalendar(models.Model):
    """Calendrier de congés."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nom du calendrier")
    description = models.TextField(blank=True, verbose_name="Description")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="calendars_created",
        verbose_name="Créé par",
    )
    sectors = models.ManyToManyField(
        Sector,
        related_name="leave_calendars",
        verbose_name="Secteurs concernés",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    visibility_end_date = models.DateField(
        verbose_name="Date de fin de visibilité",
        help_text="Le calendrier reste visible jusqu'à cette date",
    )
    notification_sent = models.BooleanField(
        default=False,
        verbose_name="Notification envoyée",
    )

    class Meta:
        verbose_name = "Calendrier de congés"
        verbose_name_plural = "Calendriers de congés"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Calcule automatiquement la date de fin de visibilité."""
        if not self.visibility_end_date:
            self.visibility_end_date = self.end_date + timedelta(days=2)
        super().save(*args, **kwargs)

    def clean(self):
        """Validation des dates."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(
                    "La date de début doit être antérieure à la date de fin."
                )

    def is_visible(self):
        """Vérifie si le calendrier est actuellement visible."""
        today = timezone.now().date()
        return self.start_date <= today <= self.visibility_end_date

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("leave:calendar_detail", kwargs={"pk": self.pk})


class LeaveRequest(models.Model):
    """Demande de congés."""

    PERIOD_CHOICES = [
        ("full", "Journée entière"),
        ("morning", "Matin"),
        ("afternoon", "Après-midi"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calendar = models.ForeignKey(
        LeaveCalendar,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="Calendrier",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name="Utilisateur",
    )
    date = models.DateField(verbose_name="Date")
    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        default="full",
        verbose_name="Période",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Demande de congés"
        verbose_name_plural = "Demandes de congés"
        ordering = ["date", "period"]
        unique_together = ["calendar", "user", "date", "period"]

    def __str__(self):
        return f"{self.user} - {self.date} ({self.get_period_display()})"

    def clean(self):
        """Vérifie que la date est dans la période du calendrier."""
        if self.date and self.calendar:
            if not (self.calendar.start_date <= self.date <= self.calendar.end_date):
                raise ValidationError(
                    "La date doit être comprise entre le début et la fin du calendrier."
                )

    def get_period_css_class(self):
        """Retourne la classe CSS pour la période."""
        return {
            "full": "leave-full",
            "morning": "leave-morning",
            "afternoon": "leave-afternoon",
        }.get(self.period, "leave-full")


class LeaveHistory(models.Model):
    """Historique des modifications des demandes de congés."""

    ACTION_CHOICES = [
        ("created", "Créé"),
        ("updated", "Modifié"),
        ("deleted", "Supprimé"),
    ]

    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history",
        verbose_name="Demande",
    )
    leave_request_info = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Infos de la demande",
        help_text="Stocké pour les suppressions quand la demande n'existe plus",
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action",
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Modifié par",
    )
    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Anciennes données",
    )
    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nouvelles données",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de modification",
    )

    class Meta:
        verbose_name = "Historique de modification"
        verbose_name_plural = "Historiques de modifications"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.leave_request} - {self.get_action_display()}"


def calculate_easter_date(year: int) -> "datetime.date":
    """Calcule la date de Pâques pour une année donnée (algorithme de Meeus/Jones/Butcher)."""
    from datetime import date

    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def populate_french_holidays(year: int):
    """Crée les jours fériés français pour une année donnée."""
    from datetime import date, timedelta

    holidays = [
        (date(year, 1, 1), "Jour de l'an"),
        (date(year, 5, 1), "Fête du Travail"),
        (date(year, 5, 8), "Victoire 1945"),
        (date(year, 7, 14), "Fête nationale"),
        (date(year, 8, 15), "Assomption"),
        (date(year, 11, 1), "Toussaint"),
        (date(year, 11, 11), "Armistice 1918"),
        (date(year, 12, 25), "Noël"),
    ]

    # Jours fériés variables
    easter = calculate_easter_date(year)
    holidays.extend(
        [
            (easter + timedelta(days=1), "Lundi de Pâques"),
            (easter + timedelta(days=39), "Jeudi de l'Ascension"),
            (easter + timedelta(days=50), "Lundi de Pentecôte"),
        ]
    )

    for holiday_date, name in holidays:
        FrenchHoliday.objects.get_or_create(
            date=holiday_date,
            defaults={"name": name, "year": year},
        )
