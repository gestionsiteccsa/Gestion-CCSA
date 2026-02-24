"""Views pour le workflow de validation des événements."""

import logging
import urllib.parse

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import DetailView, ListView

from accounts.services import NotificationService
from events.mixins import CommunicationRequiredMixin
from events.models import (Event, EventChangeLog, EventSettings,
                           EventValidation, VideoRequestLog)

logger = logging.getLogger(__name__)


class EventValidationListView(CommunicationRequiredMixin, ListView):
    """Liste des événements en attente de validation."""

    model = Event
    template_name = "events/event_validation_list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        """Filtre les événements en attente de validation.

        Optimisation: prefetch_related pour éviter les requêtes N+1.
        """
        return (
            Event.objects.filter(
                is_active=True,
            )
            .filter(Q(validation__isnull=True) | Q(validation__is_validated=False))
            .prefetch_related("sectors", "video_requests")
            .select_related("created_by")
            .order_by("created_at")
        )

    def get_context_data(self, **kwargs):
        """Ajoute les compteurs au contexte.

        Optimisation: Utilise le paginator pour le count et une seule requête
        pour les statistiques globales.
        """
        context = super().get_context_data(**kwargs)

        # Utiliser le paginator pour obtenir le count sans refaire la requête
        context["pending_count"] = (
            context["paginator"].count
            if context.get("paginator")
            else self.get_queryset().count()
        )

        # Compter les événements validés via EventValidation (is_validated=True)
        from events.models import EventValidation

        context["validated_count"] = EventValidation.objects.filter(
            event__is_active=True, is_validated=True
        ).count()

        context["rejected_count"] = (
            EventValidation.objects.filter(event__is_active=True, is_validated=False)
            .exclude(validated_by__isnull=True)
            .count()
        )

        return context


class EventValidationDetailView(CommunicationRequiredMixin, DetailView):
    """Détail d'un événement pour validation."""

    model = Event
    template_name = "events/event_validation.html"
    context_object_name = "event"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Inclut les relations pour optimisation."""
        return Event.objects.filter(is_active=True).prefetch_related(
            "sectors", "created_by"
        )

    def _get_validation_status(self, validation):
        """Retourne le statut textuel de la validation."""
        if not validation:
            return "pending"
        if validation.is_validated:
            return "validated"
        if validation.validated_by:
            return "rejected"
        return "pending"

    def get_context_data(self, **kwargs):
        """Ajoute les données de validation au contexte."""
        context = super().get_context_data(**kwargs)

        # Vérifier si une validation existe déjà
        try:
            validation = self.object.validation
            context["validation"] = validation
            context["validation_status"] = self._get_validation_status(validation)
        except EventValidation.DoesNotExist:
            context["validation"] = None
            context["validation_status"] = "pending"

        # Récupérer les demandes vidéo en une seule requête
        video_requests = list(
            VideoRequestLog.objects.filter(event=self.object).order_by("-sent_at")
        )
        context["video_requests"] = video_requests
        context["latest_video_request"] = video_requests[0] if video_requests else None

        # Vérifier si on peut envoyer plus de demandes (max 4)
        total_requests = len(video_requests)
        context["can_send_more"] = total_requests < 4
        context["total_requests"] = total_requests

        # Récupérer l'email de notification vidéo configuré
        context["video_email"] = EventSettings.get_video_email()

        # Construire les URLs de partage sur les réseaux sociaux
        site_url = getattr(settings, "SITE_URL", "")
        event_url = f"{site_url}{self.object.get_absolute_url()}"
        encoded_event_url = urllib.parse.quote(event_url, safe="")

        # URL de création d'événement Facebook
        context["facebook_url"] = "https://www.facebook.com/events/create/"

        # URL de partage Facebook
        context["facebook_share_url"] = (
            f"https://www.facebook.com/sharer/sharer.php?u={encoded_event_url}"
        )

        # URL de partage LinkedIn
        context["linkedin_share_url"] = (
            f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_event_url}"
        )

        return context

    def post(self, request, *args, **kwargs):
        """Gère la validation ou le rejet de l'événement."""
        self.object = self.get_object()
        action = request.POST.get("action")
        comment = request.POST.get("comment", "")

        if action not in ["validate", "reject"]:
            messages.error(request, "Action invalide.")
            return redirect(self.object.get_validation_url())

        with transaction.atomic():
            # Créer ou mettre à jour la validation
            validation, created = EventValidation.objects.get_or_create(
                event=self.object,
                defaults={
                    "validated_by": request.user,
                },
            )

            if action == "validate":
                validation.is_validated = True
                validation.validated_at = timezone.now()
                message = "L'événement a été validé avec succès."
                log_action = "validate"
                status_text = "validé"
            else:
                validation.is_validated = False
                validation.validated_at = None
                message = "L'événement a été rejeté."
                log_action = "reject"
                status_text = "rejeté"

            validation.validated_by = request.user
            validation.notes = comment
            validation.save()
            self.object.save()

            # Créer un log
            EventChangeLog.objects.create(
                event=self.object,
                changed_by=request.user,
                field_name=log_action,
                old_value="",
                new_value=f"Statut: {status_text}, Commentaire: {comment}",
            )

            # Envoyer un email au créateur
            self._send_validation_email(validation, action, comment)

            # Envoyer une notification système
            if action == "validate":
                NotificationService.notify_event_validated(self.object, request.user)
            else:
                NotificationService.notify_event_rejected(
                    self.object, request.user, comment
                )

            messages.success(request, message)
            return redirect("events:event_validation_list")

    def _send_validation_email(self, validation, action, comment):
        """Envoie un email au créateur après validation/rejet."""
        event = validation.event
        creator = event.created_by

        if not creator.email:
            return

        status_text = "validé" if action == "validate" else "rejeté"
        subject = f"Votre événement '{event.title}' a été {status_text}"

        # Construire l'URL de l'événement
        site_url = getattr(settings, "SITE_URL", "https://ccsa.example.com")
        event_url = f"{site_url}{event.get_absolute_url()}"

        context = {
            "event": event,
            "validation": validation,
            "user": creator,  # Renommé pour correspondre au template
            "action": action,
            "comment": comment,
            "site_url": site_url,
            "event_url": event_url,
        }

        html_message = render_to_string("events/emails/event_validated.html", context)
        # Générer une version texte simple
        plain_message = f"""Bonjour {creator.first_name or creator.email},

Votre événement '{event.title}' a été {status_text} par l'équipe Communication.

Détails de l'événement :
- Date : {event.start_datetime.strftime('%d/%m/%Y')}
- Heure : {event.start_datetime.strftime('%H:%M')}
- Lieu : {event.location}{f", {event.city}" if event.city else ""}
"""
        if comment:
            plain_message += f"\nCommentaire : {comment}\n"

        plain_message += f"\nVous pouvez consulter votre événement ici : {event_url}\n\nCordialement,\nL'équipe Communication"

        try:
            from_email = EventSettings.get_default_from_email()
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[creator.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Log l'erreur mais ne pas bloquer le processus
            logger.error(
                f"Erreur lors de l'envoi de l'email de validation pour l'événement {event.id}: {e}",
                exc_info=True,
            )
