"""Service de notification pour les demandes de tournage vidéo."""

from django.urls import reverse

from accounts.notifications.base import NotificationServiceBase


class VideoNotificationService(NotificationServiceBase):
    """Service de notification spécialisé pour les demandes de tournage vidéo.
    
    Gère les notifications liées au workflow vidéo :
    demande envoyée, confirmation, refus, relances.
    """

    @staticmethod
    def notify_video_refused(video_request, event):
        """Notifie l'équipe Communication quand un cameraman refuse."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        VideoNotificationService.notify_communication_team(
            notification_type="video_refused",
            title=f"Tournage refusé - {event.title}",
            message=f'Le cameraman a refusé la demande de tournage vidéo pour "{event.title}".',
            event=event,
            video_request=video_request,
            link=link,
        )

    @staticmethod
    def notify_video_confirmed(video_request, event):
        """Notifie l'équipe Communication quand un cameraman confirme."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        VideoNotificationService.notify_communication_team(
            notification_type="video_confirmed",
            title=f"Tournage confirmé - {event.title}",
            message=f'Le cameraman a confirmé sa participation au tournage vidéo pour "{event.title}".',
            event=event,
            video_request=video_request,
            link=link,
        )

    @staticmethod
    def notify_video_request_sent(
        video_request, event, is_relance=False, relance_num=0
    ):
        """Notifie l'équipe Communication quand une demande de tournage est envoyée."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        if is_relance:
            title = f"Relance n°{relance_num} envoyée - {event.title}"
            message = f'Une relance (n°{relance_num}) a été envoyée au cameraman pour le tournage de "{event.title}".'
        else:
            title = f"Demande de tournage envoyée - {event.title}"
            message = f'Une demande de tournage vidéo a été envoyée au cameraman pour "{event.title}".'

        VideoNotificationService.notify_communication_team(
            notification_type="video_request_sent",
            title=title,
            message=message,
            event=event,
            video_request=video_request,
            link=link,
        )
