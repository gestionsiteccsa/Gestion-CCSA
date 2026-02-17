"""Services pour l'app accounts."""

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from accounts.models import Notification, User, UserNotificationPreference
from events.models import Event, VideoRequestLog


class NotificationService:
    """Service pour gerer les notifications avec respect des preferences."""

    # Mapping des types de notification vers les labels
    NOTIFICATION_LABELS = {
        "video_refused": "Refus de tournage",
        "video_confirmed": "Confirmation de tournage",
        "event_created": "Nouvel événement",
        "event_updated": "Événement modifié",
        "event_deleted": "Événement supprimé",
        "event_commented": "Nouveau commentaire",
        "event_validated": "Événement validé",
        "event_rejected": "Événement rejeté",
        "video_request_sent": "Demande de tournage",
    }

    @staticmethod
    def notify_user(
        user,
        notification_type,
        title,
        message,
        event=None,
        video_request=None,
        link="",
        send_email=True,
    ):
        """
        Notifie un utilisateur specifique en respectant ses preferences.
        """
        # Verifier si la notification in-app est autorisee
        if UserNotificationPreference.is_notification_allowed(
            user, notification_type, "in_app"
        ):
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                event=event,
                video_request=video_request,
                link=link,
            )

        # Verifier si l'email est autorise
        if send_email and UserNotificationPreference.is_notification_allowed(
            user, notification_type, "email"
        ):
            NotificationService._send_email_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                event=event,
                link=link,
            )

    @staticmethod
    def _send_email_notification(
        user, notification_type, title, message, event=None, link=""
    ):
        """Envoie une notification par email avec template HTML."""
        try:
            # Construire l'URL absolue
            if link and not link.startswith("http"):
                link = f"{settings.SITE_URL}{link}"

            # URL des préférences
            preferences_url = (
                f"{settings.SITE_URL}{reverse('accounts:notification_preferences')}"
            )

            # Préparer le contexte pour le template
            context = {
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "notification_label": NotificationService.NOTIFICATION_LABELS.get(
                    notification_type, "Notification"
                ),
                "link": link,
                "preferences_url": preferences_url,
                "user": user,
            }

            # Ajouter les détails de l'événement si présent
            if event:
                context["event"] = event
                context["sectors"] = ", ".join([s.name for s in event.sectors.all()])
                template_name = "accounts/emails/notification_event.html"
            else:
                template_name = "accounts/emails/notification_base.html"

            # Rendre le template HTML
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            # Envoyer l'email
            send_mail(
                subject=f"[Gestion CCSA] {title}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Log l'erreur mais ne bloque pas le processus
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erreur d'envoi d'email à {user.email}: {str(e)}")

    @staticmethod
    def notify_communication_team(
        notification_type,
        title,
        message,
        event=None,
        video_request=None,
        link="",
        send_email=True,
    ):
        """
        Notifie tous les membres de l'equipe Communication en respectant leurs preferences.
        """
        communication_users = User.objects.filter(
            user_roles__role__name="Communication", user_roles__is_active=True
        ).distinct()

        for user in communication_users:
            NotificationService.notify_user(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                event=event,
                video_request=video_request,
                link=link,
                send_email=send_email,
            )

    @staticmethod
    def notify_video_refused(video_request, event):
        """Notifie l'equipe Communication quand un cameraman refuse."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        NotificationService.notify_communication_team(
            notification_type="video_refused",
            title=f"Tournage refusé - {event.title}",
            message=f'Le cameraman a refusé la demande de tournage vidéo pour "{event.title}".',
            event=event,
            video_request=video_request,
            link=link,
        )

    @staticmethod
    def notify_video_confirmed(video_request, event):
        """Notifie l'equipe Communication quand un cameraman confirme."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        NotificationService.notify_communication_team(
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
        """Notifie l'equipe Communication quand une demande de tournage est envoyee."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        if is_relance:
            title = f"Relance n°{relance_num} envoyée - {event.title}"
            message = f'Une relance (n°{relance_num}) a été envoyée au cameraman pour le tournage de "{event.title}".'
        else:
            title = f"Demande de tournage envoyée - {event.title}"
            message = f'Une demande de tournage vidéo a été envoyée au cameraman pour "{event.title}".'

        NotificationService.notify_communication_team(
            notification_type="video_request_sent",
            title=title,
            message=message,
            event=event,
            video_request=video_request,
            link=link,
        )

    @staticmethod
    def notify_event_created(event, created_by):
        """Notifie l'equipe Communication quand un evenement est cree."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        NotificationService.notify_communication_team(
            notification_type="event_created",
            title=f"Nouvel événement - {event.title}",
            message=f'Un nouvel événement "{event.title}" a été créé par {created_by.get_full_name() or created_by.email}.',
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_updated(event, updated_by):
        """Notifie l'equipe Communication quand un evenement est modifie."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        NotificationService.notify_communication_team(
            notification_type="event_updated",
            title=f"Événement modifié - {event.title}",
            message=f'L\'événement "{event.title}" a été modifié par {updated_by.get_full_name() or updated_by.email}.',
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_deleted(event_title, deleted_by):
        """Notifie l'equipe Communication quand un evenement est supprime."""
        link = reverse("events:event_list")

        NotificationService.notify_communication_team(
            notification_type="event_deleted",
            title=f"Événement supprimé - {event_title}",
            message=f'L\'événement "{event_title}" a été supprimé par {deleted_by.get_full_name() or deleted_by.email}.',
            link=link,
        )

    @staticmethod
    def notify_event_commented(comment):
        """Notifie l'equipe Communication et le createur de l'evenement."""
        event = comment.event
        author = comment.author
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        # Notifier l'equipe Communication
        NotificationService.notify_communication_team(
            notification_type="event_commented",
            title=f"Nouveau commentaire - {event.title}",
            message=f'{author.get_full_name() or author.email} a commenté l\'événement "{event.title}".',
            event=event,
            link=link,
        )

        # Notifier le createur de l'evenement (s'il n'est pas l'auteur du commentaire)
        if event.created_by != author:
            NotificationService.notify_user(
                user=event.created_by,
                notification_type="event_commented",
                title=f"Nouveau commentaire sur votre événement - {event.title}",
                message=f'{author.get_full_name() or author.email} a commenté votre événement "{event.title}".',
                event=event,
                link=link,
            )

    @staticmethod
    def notify_event_validated(event, validated_by):
        """Notifie le createur de l'evenement quand il est valide."""
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        NotificationService.notify_user(
            user=event.created_by,
            notification_type="event_validated",
            title=f"Événement validé - {event.title}",
            message=f'Votre événement "{event.title}" a été validé par {validated_by.get_full_name() or validated_by.email}.',
            event=event,
            link=link,
        )

        # Notifier aussi l'equipe Communication
        NotificationService.notify_communication_team(
            notification_type="event_validated",
            title=f"Événement validé - {event.title}",
            message=f'L\'événement "{event.title}" a été validé par {validated_by.get_full_name() or validated_by.email}.',
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_rejected(event, rejected_by, reason=""):
        """Notifie le createur de l'evenement quand il est rejete."""
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        message = f'Votre événement "{event.title}" a été rejeté par {rejected_by.get_full_name() or rejected_by.email}.'
        if reason:
            message += f"\n\nMotif : {reason}"

        NotificationService.notify_user(
            user=event.created_by,
            notification_type="event_rejected",
            title=f"Événement rejeté - {event.title}",
            message=message,
            event=event,
            link=link,
        )

        # Notifier aussi l'equipe Communication
        comm_message = f'L\'événement "{event.title}" a été rejeté par {rejected_by.get_full_name() or rejected_by.email}.'
        if reason:
            comm_message += f"\n\nMotif : {reason}"

        NotificationService.notify_communication_team(
            notification_type="event_rejected",
            title=f"Événement rejeté - {event.title}",
            message=comm_message,
            event=event,
            link=link,
        )
