"""Views pour le workflow de demandes de tournage vidéo."""

import logging
from functools import wraps
from smtplib import SMTPException
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from accounts.models import Role, UserRole
from accounts.services import NotificationService
from events.forms import VideoNotificationSettingsForm
from events.mixins import CommunicationRequiredMixin
from events.models import (
    Event,
    EventSettings,
    VideoNotificationSettings,
    VideoRequestLog,
)

logger = logging.getLogger(__name__)


def ratelimit(key="ip", rate="10/m", block=False):
    """Décorateur de rate limiting simple basé sur le cache Django."""

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Générer la clé de cache
            if key == "user":
                if request.user.is_authenticated:
                    cache_key = f"ratelimit_{func.__name__}_user_{request.user.id}"
                else:
                    cache_key = f'ratelimit_{func.__name__}_ip_{request.META.get("REMOTE_ADDR", "unknown")}'
            else:
                cache_key = f'ratelimit_{func.__name__}_ip_{request.META.get("REMOTE_ADDR", "unknown")}'

            # Parser le rate (ex: '10/m' -> 10 requêtes par minute)
            count, period = rate.split("/")
            count = int(count)
            timeout = {"s": 1, "m": 60, "h": 3600, "d": 86400}.get(period, 60)

            # Vérifier le nombre de requêtes
            current = cache.get(cache_key, 0)
            if current >= count:
                if block:
                    return JsonResponse(
                        {"error": "Trop de requêtes. Veuillez réessayer plus tard."},
                        status=429,
                    )
                else:
                    logger.warning(f"Rate limit dépassé pour {cache_key}")
            else:
                cache.set(cache_key, current + 1, timeout)

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


class VideoEmailSettingsView(
    LoginRequiredMixin, CommunicationRequiredMixin, UpdateView
):
    """Vue pour configurer l'email de notification vidéo."""

    model = VideoNotificationSettings
    form_class = VideoNotificationSettingsForm
    template_name = "events/video_email_settings.html"
    success_url = reverse_lazy("events:video_email_settings")

    def get_object(self, queryset=None):
        """Récupère ou crée les paramètres.

        Ne crée pas avec d'email par défaut - doit être configuré manuellement.
        """
        settings_obj, created = VideoNotificationSettings.objects.get_or_create(
            pk=1, defaults={}
        )
        return settings_obj

    def form_valid(self, form):
        """Sauvegarde les paramètres avec l'utilisateur qui a modifié."""
        form.instance.updated_by = self.request.user
        messages.success(
            self.request, "L'email de notification vidéo a été mis à jour."
        )
        return super().form_valid(form)


@login_required
@ratelimit(key="user", rate="5/m", block=True)
def send_video_request(request, slug):
    """Envoie une demande de tournage vidéo par email."""
    event = get_object_or_404(Event, slug=slug)

    # Vérifier que l'utilisateur a le rôle Communication
    try:
        communication_role = Role.objects.get(name="Communication", is_active=True)
        if not UserRole.objects.filter(
            user=request.user, role=communication_role, is_active=True
        ).exists():
            messages.error(
                request, "Vous n'avez pas la permission d'envoyer cette demande."
            )
            return redirect("events:event_validation", slug=event.slug)
    except Role.DoesNotExist:
        messages.error(request, "Rôle Communication non trouvé.")
        return redirect("events:event_validation", slug=event.slug)

    # Vérifier que l'événement demande un tournage
    if not event.needs_filming:
        messages.error(request, "Cet événement ne demande pas de tournage vidéo.")
        return redirect("events:event_validation")

    # Récupérer l'email configuré
    recipient_email = EventSettings.get_video_email()
    if not recipient_email:
        messages.error(request, "Aucun email de notification vidéo n'est configuré.")
        return redirect("events:video_email_settings")

    # Récupérer le commentaire optionnel (max 500 caractères)
    comment = request.POST.get("comment", "").strip()[:500]

    # Vérifier les demandes précédentes pour les relances
    previous_requests = VideoRequestLog.objects.filter(event=event).order_by("-sent_at")
    total_requests = previous_requests.count()

    # Vérifier la limite de 3 relances (4 demandes max au total)
    if total_requests >= 4:
        messages.error(
            request, "Vous avez atteint la limite de 3 relances pour cet événement."
        )
        return redirect("events:event_validation", slug=event.slug)

    # Si c'est une relance (au moins une demande précédente non confirmée)
    is_relance = False
    if total_requests > 0:
        latest_request = previous_requests.first()
        if not latest_request.confirmed:
            is_relance = True
            # Ajouter le préfixe [RELANCE] au commentaire
            if comment:
                comment = f"[RELANCE #{total_requests}] {comment}"
            else:
                comment = f"[RELANCE #{total_requests}]"

    # Préparer le contexte de l'email
    context = {
        "event": event,
        "sent_by": request.user,
        "event_url": request.build_absolute_uri(event.get_absolute_url()),
        "comment": comment,
    }

    # Créer l'enregistrement dans l'historique AVANT d'envoyer l'email pour avoir le token
    video_request_log = VideoRequestLog.objects.create(
        event=event,
        sent_by=request.user,
        recipient_email=recipient_email,
        status="sent",
        comment=comment,
    )

    # Générer l'URL de confirmation
    confirmation_url = request.build_absolute_uri(
        reverse(
            "events:confirm_video_request",
            kwargs={"token": video_request_log.confirmation_token},
        )
    )

    # Mettre à jour le contexte avec l'URL de confirmation
    context["confirmation_url"] = confirmation_url

    # Générer les URLs pour les agendas
    event_title = f"Tournage vidéo - {event.title}"
    event_description = f"Tournage vidéo pour l'événement : {event.title}"
    event_location = f"{event.location}{', ' + event.city if event.city else ''}"

    # Format des dates pour Google Calendar
    start_str = event.start_datetime.strftime("%Y%m%dT%H%M%S")
    end_str = (
        event.end_datetime.strftime("%Y%m%dT%H%M%S")
        if event.end_datetime
        else event.start_datetime.strftime("%Y%m%dT%H%M%S")
    )

    # URL Google Calendar
    google_params = {
        "action": "TEMPLATE",
        "text": event_title,
        "dates": f"{start_str}/{end_str}",
        "details": event_description,
        "location": event_location,
    }
    context["google_calendar_url"] = (
        f"https://calendar.google.com/calendar/render?{urlencode(google_params)}"
    )

    # URL Outlook
    outlook_params = {
        "subject": event_title,
        "startdt": event.start_datetime.isoformat(),
        "enddt": (
            event.end_datetime.isoformat()
            if event.end_datetime
            else event.start_datetime.isoformat()
        ),
        "body": event_description,
        "location": event_location,
    }
    context["outlook_calendar_url"] = (
        f"https://outlook.live.com/calendar/0/deeplink/compose?{urlencode(outlook_params)}"
    )

    # URL de téléchargement ICS
    context["ics_download_url"] = request.build_absolute_uri(
        reverse("events:download_ics", kwargs={"slug": event.slug})
    )

    # URL de refus (pour le bouton "Refuser")
    refuse_url = request.build_absolute_uri(
        reverse(
            "events:refuse_video_request",
            kwargs={"token": video_request_log.confirmation_token},
        )
    )
    context["refuse_url"] = refuse_url

    # URL du site pour les images statiques
    context["site_url"] = request.build_absolute_uri("/")

    # Envoyer l'email
    try:
        subject = f"Demande de tournage vidéo - {event.title}"
        message = render_to_string("events/emails/video_request.txt", context)
        html_message = render_to_string("events/emails/video_request.html", context)

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # Utilise DEFAULT_FROM_EMAIL
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )

        # Message différent selon s'il s'agit d'une relance ou d'une première demande
        if is_relance:
            messages.success(
                request,
                f"Relance n°{total_requests} envoyée à {recipient_email}. "
                f"Il reste {4 - (total_requests + 1)} tentative(s).",
            )
        else:
            messages.success(
                request,
                f"La demande de tournage vidéo a été envoyée à {recipient_email}.",
            )

        # Créer une notification pour l'équipe Communication
        NotificationService.notify_video_request_sent(
            video_request=video_request_log,
            event=event,
            is_relance=is_relance,
            relance_num=total_requests if is_relance else 0,
        )

        # Envoyer une copie de l'email au cameraman configuré
        try:
            cameraman_email = EventSettings.get_video_email()
            if cameraman_email and cameraman_email != recipient_email:
                # Renvoyer l'email au cameraman
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[cameraman_email],
                    html_message=html_message,
                    fail_silently=True,
                )
        except Exception as e:
            logger.error(f"Erreur envoi email au cameraman: {e}")

    except SMTPException as e:
        # Enregistrer l'échec
        VideoRequestLog.objects.create(
            event=event,
            sent_by=request.user,
            recipient_email=recipient_email,
            status="failed",
        )
        messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
        return redirect("events:event_validation", slug=event.slug)

    return redirect("events:event_validation", slug=event.slug)


@ratelimit(key="ip", rate="10/m", block=True)
def confirm_video_request(request, token):
    """Vue publique pour que le caméraman confirme sa participation."""
    from django.utils import timezone

    # Récupérer la demande par son token (avec select_related pour éviter N+1)
    video_request = get_object_or_404(
        VideoRequestLog.objects.select_related("event"), confirmation_token=token
    )
    event = video_request.event

    # Générer les URLs pour les agendas
    event_title = f"Tournage vidéo - {event.title}"
    event_description = f"Tournage vidéo pour l'événement : {event.title}"
    event_location = f"{event.location}{', ' + event.city if event.city else ''}"

    # Format des dates pour Google Calendar
    start_str = event.start_datetime.strftime("%Y%m%dT%H%M%S")
    end_str = (
        event.end_datetime.strftime("%Y%m%dT%H%M%S")
        if event.end_datetime
        else event.start_datetime.strftime("%Y%m%dT%H%M%S")
    )

    # URL Google Calendar
    google_params = {
        "action": "TEMPLATE",
        "text": event_title,
        "dates": f"{start_str}/{end_str}",
        "details": event_description,
        "location": event_location,
    }
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?{urlencode(google_params)}"
    )

    # URL Outlook
    outlook_params = {
        "subject": event_title,
        "startdt": event.start_datetime.isoformat(),
        "enddt": (
            event.end_datetime.isoformat()
            if event.end_datetime
            else event.start_datetime.isoformat()
        ),
        "body": event_description,
        "location": event_location,
    }
    outlook_calendar_url = f"https://outlook.live.com/calendar/0/deeplink/compose?{urlencode(outlook_params)}"

    # Vérifier si déjà confirmé
    if video_request.confirmed:
        return render(
            request,
            "events/video_request_confirmed.html",
            {
                "video_request": video_request,
                "already_confirmed": True,
                "event": event,
                "google_calendar_url": google_calendar_url,
                "outlook_calendar_url": outlook_calendar_url,
            },
        )

    # Marquer comme confirmé
    video_request.confirmed = True
    video_request.confirmed_at = timezone.now()
    video_request.save()

    # Notifier l'équipe Communication
    NotificationService.notify_video_confirmed(video_request, event)

    return render(
        request,
        "events/video_request_confirmed.html",
        {
            "video_request": video_request,
            "already_confirmed": False,
            "event": event,
            "google_calendar_url": google_calendar_url,
            "outlook_calendar_url": outlook_calendar_url,
        },
    )


@ratelimit(key="ip", rate="10/m", block=True)
def refuse_video_request(request, token):
    """Vue publique pour que le caméraman refuse la participation."""
    from django.utils import timezone

    # Récupérer la demande par son token (avec select_related pour éviter N+1)
    video_request = get_object_or_404(
        VideoRequestLog.objects.select_related("event"), confirmation_token=token
    )
    event = video_request.event

    # Vérifier si déjà confirmé ou refusé
    if video_request.confirmed:
        return render(
            request,
            "events/video_request_refused.html",
            {
                "video_request": video_request,
                "already_responded": True,
                "response_type": "confirmé",
                "event": event,
            },
        )

    if video_request.refused:
        return render(
            request,
            "events/video_request_refused.html",
            {
                "video_request": video_request,
                "already_responded": True,
                "response_type": "refusé",
                "event": event,
            },
        )

    # Marquer comme refusé
    video_request.refused = True
    video_request.refused_at = timezone.now()
    video_request.save()

    # Notifier l'équipe Communication
    NotificationService.notify_video_refused(video_request, event)

    return render(
        request,
        "events/video_request_refused.html",
        {
            "video_request": video_request,
            "already_responded": False,
            "event": event,
        },
    )


def escape_ics_value(value):
    r"""
    Échappe les caractères spéciaux dans une valeur ICS selon RFC 5545.

    Les caractères spéciaux à échapper sont : \, ; , et \n
    """
    if not value:
        return ""
    # Échapper les caractères spéciaux selon RFC 5545
    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "")
    return value


def generate_ics_file(event):
    """Génère le contenu d'un fichier ICS pour un événement."""

    uid = f"{event.slug}@gestion-ccsa.fr"
    from datetime import datetime

    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = event.start_datetime.strftime("%Y%m%dT%H%M%S")
    dtend = (
        event.end_datetime.strftime("%Y%m%dT%H%M%S")
        if event.end_datetime
        else event.start_datetime.strftime("%Y%m%dT%H%M%S")
    )

    summary = escape_ics_value(f"Tournage vidéo - {event.title}")
    description = escape_ics_value(f"Tournage vidéo pour l'événement : {event.title}")
    location = escape_ics_value(
        f"{event.location}{', ' + event.city if event.city else ''}"
    )

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Gestion CCSA//Event//FR
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT
END:VCALENDAR"""

    return ics_content


def download_ics(request, slug):
    """Télécharge un fichier ICS pour l'événement."""
    event = get_object_or_404(Event, slug=slug)
    ics_content = generate_ics_file(event)

    response = HttpResponse(ics_content, content_type="text/calendar")
    response["Content-Disposition"] = (
        f'attachment; filename="tournage_{event.slug}.ics"'
    )

    return response
