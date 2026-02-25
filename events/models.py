"""Modèles pour l'app events."""

import re
import uuid
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from events.validators import ImageExtensionValidator, ImageSizeValidator


class Sector(models.Model):
    """Secteur d'activité pour les événements."""

    name = models.CharField(max_length=100, verbose_name="Nom")
    color_code = models.CharField(
        max_length=7,
        verbose_name="Code couleur",
        help_text="Format hexadécimal (ex: #b4c7e7)",
    )
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Secteur"
        verbose_name_plural = "Secteurs"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        """Valide le format du code couleur."""
        if self.color_code and not re.match(r"^#[0-9A-Fa-f]{6}$", self.color_code):
            raise ValidationError(
                {"color_code": "Le code couleur doit être au format hexadécimal (#RRGGBB)"}
            )


class Event(models.Model):
    """Événement organisé par la CCSA."""

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description", blank=True)
    location = models.CharField(max_length=200, verbose_name="Lieu")
    city = models.CharField(max_length=100, verbose_name="Ville")

    # Full-text search (PostgreSQL)
    search_vector = SearchVectorField(null=True, blank=True)

    start_datetime = models.DateTimeField(verbose_name="Date et heure de début")
    end_datetime = models.DateTimeField(
        verbose_name="Date et heure de fin",
        null=True,
        blank=True,
        help_text="Optionnel - laissez vide si l'événement n'a pas de date de fin définie",
    )

    sectors = models.ManyToManyField(
        Sector,
        verbose_name="Secteurs",
        related_name="events",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Créé par",
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    # Communication en amont (checkboxes multiples)
    comm_before = models.BooleanField(default=False, verbose_name="Communication avant l'événement")
    comm_during = models.BooleanField(
        default=False, verbose_name="Communication pendant l'événement"
    )
    comm_after = models.BooleanField(default=False, verbose_name="Communication après l'événement")

    # Options additionnelles
    needs_filming = models.BooleanField(default=False, verbose_name="Intervention pour filmer")
    needs_poster = models.BooleanField(default=False, verbose_name="Demande d'affiche")

    # Notification
    notify_on_publish = models.BooleanField(
        default=False,
        verbose_name="Recevoir un email lors de la confirmation de la publication",
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["-start_datetime"]
        indexes = [
            models.Index(fields=["search_vector"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["city"]),
            models.Index(fields=["start_datetime"]),
            models.Index(fields=["end_datetime"]),
            models.Index(fields=["is_active", "start_datetime"]),
            models.Index(fields=["is_active", "start_datetime", "end_datetime"]),
            models.Index(fields=["created_by", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%d/%m/%Y')}"

    def generate_slug(self):
        """Génère un slug unique basé sur le titre et la date."""
        base_slug = slugify(self.title)
        date_str = self.start_datetime.strftime("%Y-%m-%d")
        slug = f"{base_slug}-{date_str}"

        # Vérifier l'unicité et ajouter un suffixe si nécessaire
        counter = 1
        original_slug = slug
        while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        """Sauvegarde l'événement avec génération du slug et mise à jour du search_vector."""
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

        # Mettre à jour le search_vector après la sauvegarde (PostgreSQL uniquement)
        if hasattr(self, "search_vector") and connection.vendor == "postgresql":
            Event.objects.filter(pk=self.pk).update(
                search_vector=(
                    SearchVector("title", weight="A")
                    + SearchVector("description", weight="B")
                    + SearchVector("location", weight="C")
                    + SearchVector("city", weight="C")
                )
            )

    def clean(self):
        """Valide les dates de l'événement."""
        if self.end_datetime and self.start_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError("La date de fin doit être postérieure à la date de début.")

    def get_absolute_url(self):
        """Retourne l'URL de détail de l'événement."""
        return reverse("events:event_detail", kwargs={"slug": self.slug})

    def get_ical_url(self):
        """Retourne l'URL de téléchargement iCal de l'événement."""
        return reverse("events:download_ics", kwargs={"slug": self.slug})

    def get_validation_url(self):
        """Retourne l'URL de validation de l'événement."""
        return reverse("events:event_validation", kwargs={"slug": self.slug})

    @property
    def is_upcoming(self):
        """Retourne True si l'événement est à venir."""
        return self.start_datetime > timezone.now()

    @property
    def is_ongoing(self):
        """Retourne True si l'événement est en cours."""
        now = timezone.now()
        if self.end_datetime:
            return self.start_datetime <= now <= self.end_datetime
        return self.start_datetime <= now < self.start_datetime + timedelta(hours=1)

    @property
    def is_past(self):
        """Retourne True si l'événement est passé."""
        if self.end_datetime:
            return self.end_datetime < timezone.now()
        return self.start_datetime < timezone.now()

    @property
    def is_recurring(self):
        """Retourne True si l'événement est récurrent."""
        return hasattr(self, "recurrence")


class EventImage(models.Model):
    """Image associée à un événement."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="images",
    )
    image = models.ImageField(
        upload_to="events/%Y/%m/",
        verbose_name="Image",
        validators=[
            ImageExtensionValidator(),
            ImageSizeValidator(),
        ],
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Légende",
        help_text="Description ou légende de l'image (optionnel)",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadé le")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Image d'événement"
        verbose_name_plural = "Images d'événements"
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image {self.order} de {self.event.title}"

    def clean(self):
        """Valide le nombre maximum d'images."""
        max_images = getattr(settings, "EVENTS_MAX_IMAGES", 10)
        if hasattr(self, "event") and self.event:
            current_count = EventImage.objects.filter(event=self.event).count()
            # Si c'est une création (pas de pk), on compte +1
            if not self.pk and current_count >= max_images:
                raise ValidationError(
                    f"Un événement ne peut pas avoir plus de {max_images} images."
                )


class EventComment(models.Model):
    """Commentaire sur un événement."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Auteur",
        related_name="event_comments",
    )
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.event}"


class EventChangeLog(models.Model):
    """Historique des modifications d'un événement."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="change_logs",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Modifié par",
        related_name="event_changes",
    )
    field_name = models.CharField(max_length=100, verbose_name="Champ modifié")
    old_value = models.TextField(blank=True, verbose_name="Ancienne valeur")
    new_value = models.TextField(blank=True, verbose_name="Nouvelle valeur")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Historique de modification"
        verbose_name_plural = "Historiques de modifications"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"Modification de {self.field_name} sur {self.event}"


class EventValidation(models.Model):
    """Validation d'un événement par l'équipe Communication."""

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="validation",
    )
    is_validated = models.BooleanField(default=False, verbose_name="Validé par la communication")
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Validé par",
        related_name="validated_events",
    )
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name="Validé le")
    notes = models.TextField(blank=True, verbose_name="Notes de validation")

    class Meta:
        verbose_name = "Validation d'événement"
        verbose_name_plural = "Validations d'événements"
        ordering = ["-validated_at"]
        indexes = [
            models.Index(fields=["is_validated"]),
            models.Index(fields=["event", "is_validated"]),
            models.Index(fields=["validated_at"]),
        ]

    def __str__(self):
        status = "Validé" if self.is_validated else "En attente"
        return f"{self.event.title} - {status}"


class EventDocument(models.Model):
    """Document associé à un événement (PDF, Word, Excel)."""

    DOCUMENT_TYPES = [
        ("pdf", "PDF"),
        ("word", "Word"),
        ("excel", "Excel"),
        ("other", "Autre"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="documents",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    document = models.FileField(
        upload_to="events/documents/%Y/%m/",
        verbose_name="Document",
        help_text="Formats acceptés : PDF, Word (doc/docx), Excel (xls/xlsx). Taille max : 20 Mo",
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name="Type de document",
        blank=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Uploadé par",
        related_name="uploaded_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadé le")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taille (octets)")

    class Meta:
        verbose_name = "Document d'événement"
        verbose_name_plural = "Documents d'événements"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} - {self.event.title}"

    def save(self, *args, **kwargs):
        """Détecte automatiquement le type de document."""
        if self.document:
            filename = self.document.name.lower()
            if filename.endswith(".pdf"):
                self.document_type = "pdf"
            elif filename.endswith((".doc", ".docx")):
                self.document_type = "word"
            elif filename.endswith((".xls", ".xlsx")):
                self.document_type = "excel"
            else:
                self.document_type = "other"

            # Calculer la taille du fichier
            if hasattr(self.document, "size"):
                self.file_size = self.document.size

        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Retourne la taille du fichier formatée."""
        if not self.file_size:
            return "0 B"

        file_size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if file_size < 1024.0:
                return f"{file_size:.1f} {unit}"
            file_size /= 1024.0
        return f"{file_size:.1f} TB"

    def clean(self):
        """Valide le type et la taille du fichier."""
        if self.document:
            # Vérifier l'extension
            allowed_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]
            filename = self.document.name.lower()
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    f"Extension non autorisée. Extensions acceptées : {', '.join(allowed_extensions)}"
                )

            # Vérifier la taille (max 20 Mo)
            max_size = 20 * 1024 * 1024  # 20 Mo
            if hasattr(self.document, "size") and self.document.size > max_size:
                raise ValidationError("La taille du fichier ne doit pas dépasser 20 Mo.")


class EventRecurrence(models.Model):
    """Configuration de la récurrence d'un événement."""

    RECURRENCE_TYPES = [
        ("daily", "Quotidien"),
        ("weekly", "Hebdomadaire"),
        ("monthly", "Mensuel"),
        ("yearly", "Annuel"),
    ]

    DAYS_OF_WEEK = [
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
        (6, "Dimanche"),
    ]

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement parent",
        related_name="recurrence",
    )
    recurrence_type = models.CharField(
        max_length=20,
        choices=RECURRENCE_TYPES,
        verbose_name="Type de récurrence",
        default="weekly",
    )
    interval = models.PositiveIntegerField(
        default=1,
        verbose_name="Intervalle",
        help_text="Tous les X jours/semaines/mois/années",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
        help_text="Laissez vide pour une récurrence sans fin",
    )
    days_of_week = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Jours de la semaine",
        help_text="Pour la récurrence hebdomadaire : 0,1,2 pour Lundi,Mardi,Mercredi",
    )
    day_of_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Jour du mois",
        help_text="Pour la récurrence mensuelle (1-31)",
    )
    month_of_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Mois de l'année",
        help_text="Pour la récurrence annuelle (1-12)",
    )
    max_occurrences = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre maximum d'occurrences",
        help_text="Laissez vide pour illimité",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Récurrence d'événement"
        verbose_name_plural = "Récurrences d'événements"

    def __str__(self):
        return f"{self.event.title} - {self.get_recurrence_type_display()}"

    def get_days_of_week_list(self):
        """Retourne la liste des jours de la semaine."""
        if not self.days_of_week:
            return []
        return [int(d) for d in self.days_of_week.split(",") if d.isdigit()]

    def generate_occurrences(self, start_from=None, count=None):
        """Génère les occurrences de l'événement."""
        occurrences = []
        parent_event = self.event

        # Date de départ
        if start_from:
            current_date = start_from
        else:
            current_date = parent_event.start_datetime.date()

        # Heures de l'événement parent
        start_time = parent_event.start_datetime.time()
        end_time = parent_event.end_datetime.time() if parent_event.end_datetime else None

        # Nombre d'occurrences à générer
        max_count = count or self.max_occurrences or 52  # Par défaut, 1 an max
        generated_count = 0

        while generated_count < max_count:
            # Vérifier la date de fin
            if self.end_date and current_date > self.end_date:
                break

            # Vérifier si on doit générer pour cette date
            should_generate = False

            if self.recurrence_type == "daily":
                should_generate = True
            elif self.recurrence_type == "weekly":
                days = self.get_days_of_week_list()
                if not days or current_date.weekday() in days:
                    should_generate = True
            elif self.recurrence_type == "monthly":
                day = self.day_of_month or parent_event.start_datetime.day
                if current_date.day == day:
                    should_generate = True
            elif self.recurrence_type == "yearly":
                month = self.month_of_year or parent_event.start_datetime.month
                day = parent_event.start_datetime.day
                if current_date.month == month and current_date.day == day:
                    should_generate = True

            if should_generate and current_date > parent_event.start_datetime.date():
                # Créer l'occurrence
                start_datetime = datetime.combine(current_date, start_time)
                end_datetime = datetime.combine(current_date, end_time) if end_time else None

                occurrence = Event(
                    title=parent_event.title,
                    description=parent_event.description,
                    location=parent_event.location,
                    city=parent_event.city,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    created_by=parent_event.created_by,
                    comm_before=parent_event.comm_before,
                    comm_during=parent_event.comm_during,
                    comm_after=parent_event.comm_after,
                    needs_filming=parent_event.needs_filming,
                    needs_poster=parent_event.needs_poster,
                    notify_on_publish=parent_event.notify_on_publish,
                    is_active=True,
                )
                occurrence.save()

                # Copier les secteurs
                occurrence.sectors.set(parent_event.sectors.all())

                occurrences.append(occurrence)
                generated_count += 1

            # Avancer d'un jour
            current_date += timedelta(days=1)

            # Pour les récurrences non quotidiennes, optimiser
            if self.recurrence_type == "weekly" and self.get_days_of_week_list():
                # Avancer directement au prochain jour de la semaine
                while current_date.weekday() not in self.get_days_of_week_list():
                    current_date += timedelta(days=1)
                    if self.end_date and current_date > self.end_date:
                        break
            elif self.recurrence_type == "monthly":
                # Passer au mois suivant si on a dépassé le jour du mois
                day = self.day_of_month or parent_event.start_datetime.day
                if current_date.day > day:
                    # Passer au mois suivant
                    if current_date.month == 12:
                        current_date = current_date.replace(
                            year=current_date.year + 1, month=1, day=1
                        )
                    else:
                        current_date = current_date.replace(month=current_date.month + 1, day=1)
                    # Aller au jour souhaité
                    try:
                        current_date = current_date.replace(day=day)
                    except ValueError:
                        # Jour inexistant dans ce mois (ex: 31 février)
                        pass
            elif self.recurrence_type == "yearly":
                # Passer à l'année suivante
                if current_date.month > (self.month_of_year or parent_event.start_datetime.month):
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)

        return occurrences


class EventOccurrence(models.Model):
    """Lien entre un événement parent et ses occurrences générées."""

    parent_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement parent",
        related_name="occurrences",
    )
    occurrence = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Occurrence",
        related_name="parent_occurrence",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Occurrence d'événement"
        verbose_name_plural = "Occurrences d'événements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Occurrence de {self.parent_event.title} - {self.occurrence.start_datetime.strftime('%d/%m/%Y')}"


class VideoNotificationSettings(models.Model):
    """Paramètres pour l'email de notification vidéo."""

    email = models.EmailField(
        verbose_name="Email de notification",
        help_text="Adresse email qui recevra les demandes de tournage vidéo",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modifié par",
        related_name="video_settings_updates",
    )

    class Meta:
        verbose_name = "Paramètre de notification vidéo"
        verbose_name_plural = "Paramètres de notification vidéo"

    def __str__(self):
        return f"Email de notification vidéo : {self.email}"

    @classmethod
    def get_email(cls):
        """Retourne l'email configuré ou None."""
        settings_obj = cls.objects.first()
        return settings_obj.email if settings_obj else None


class VideoRequestLog(models.Model):
    """Historique des demandes de tournage vidéo envoyées."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        related_name="video_requests",
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Envoyé par",
        related_name="sent_video_requests",
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Envoyé le")
    recipient_email = models.EmailField(verbose_name="Email destinataire")
    status = models.CharField(
        max_length=20,
        choices=[
            ("sent", "Envoyé"),
            ("failed", "Échec"),
        ],
        default="sent",
        verbose_name="Statut",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaire",
        help_text="Commentaire optionnel pour la demande de tournage (max 500 caractères)",
        max_length=500,
    )
    confirmed = models.BooleanField(
        default=False,
        verbose_name="Validé par le caméraman",
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date de validation",
    )
    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        verbose_name="Token de confirmation",
    )
    refused = models.BooleanField(
        default=False,
        verbose_name="Refuse par le cameraman",
    )
    refused_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date de refus",
    )

    class Meta:
        verbose_name = "Demande de tournage vidéo"
        verbose_name_plural = "Demandes de tournage vidéo"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["event", "-sent_at"]),
            models.Index(fields=["confirmation_token"]),
        ]

    def __str__(self):
        return f"Demande vidéo pour {self.event.title} - {self.sent_at.strftime('%d/%m/%Y %H:%M')}"


class EventSettings(models.Model):
    """Paramètres globaux de l'application Événements.

    Singleton pattern - Une seule instance (pk=1) stockant tous les paramètres.
    Accessible uniquement par les superadmins via l'interface d'administration.
    """

    # Email de notification vidéo
    video_notification_email = models.EmailField(
        verbose_name="Email de notification vidéo",
        help_text="Adresse email qui recevra les demandes de tournage vidéo",
        default="j.brechoire@cc-sudavesnois.fr",
    )

    # Paramètres d'événements
    max_events_per_user = models.PositiveIntegerField(
        verbose_name="Nombre maximum d'événements par utilisateur",
        help_text="Limite le nombre d'événements qu'un utilisateur peut créer",
        default=50,
    )

    max_images_per_event = models.PositiveIntegerField(
        verbose_name="Nombre maximum d'images par événement",
        help_text="Limite le nombre d'images qu'un événement peut contenir",
        default=10,
    )

    # Paramètres de validation
    auto_validate_events = models.BooleanField(
        verbose_name="Validation automatique",
        help_text="Si activé, les événements seront automatiquement validés sans passer par la file d'attente",
        default=False,
    )

    # Paramètres d'email
    default_from_email = models.EmailField(
        verbose_name="Email d'expédition",
        help_text="Adresse email utilisée pour envoyer les notifications",
        default="j.brechoire@cc-sudavesnois.fr",
    )

    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modifié par",
        related_name="event_settings_updates",
    )

    class Meta:
        verbose_name = "Paramètres des événements"
        verbose_name_plural = "Paramètres des événements"

    def __str__(self):
        return "Paramètres des événements"

    @classmethod
    def get_settings(cls):
        """Retourne les paramètres (crée par défaut si inexistant).

        Returns:
            EventSettings: L'instance unique des paramètres
        """
        settings_obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "video_notification_email": "j.brechoire@cc-sudavesnois.fr",
                "max_events_per_user": 50,
                "max_images_per_event": 10,
                "auto_validate_events": False,
                "default_from_email": "j.brechoire@cc-sudavesnois.fr",
            },
        )
        return settings_obj

    @classmethod
    def get_video_email(cls):
        """Retourne l'email de notification vidéo.

        Returns:
            str: L'email configuré dans VideoNotificationSettings ou None
        """
        # Utiliser VideoNotificationSettings qui est le modèle utilisé par l'interface de configuration
        return VideoNotificationSettings.get_email()

    @classmethod
    def get_default_from_email(cls):
        """Retourne l'email d'expédition par défaut.

        Returns:
            str: L'email d'expédition configuré
        """
        return cls.get_settings().default_from_email
