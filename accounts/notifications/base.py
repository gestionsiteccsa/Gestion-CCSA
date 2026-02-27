"""Service de notification de base avec respect des préférences."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from accounts.models import Notification, User, UserNotificationPreference


class NotificationServiceBase:
    """Service de base pour gérer les notifications.
    
    Respecte les préférences utilisateur et fournit les méthodes
    fondamentales pour l'envoi de notifications.
    """

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
        """Notifie un utilisateur spécifique en respectant ses préférences."""
        # Vérifier si la notification in-app est autorisée
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

        # Vérifier si l'email est autorisé
        if send_email and UserNotificationPreference.is_notification_allowed(
            user, notification_type, "email"
        ):
            NotificationServiceBase._send_email_notification(
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
                "notification_label": NotificationServiceBase.NOTIFICATION_LABELS.get(
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
        """Notifie tous les membres de l'équipe Communication."""
        communication_users = User.objects.filter(
            user_roles__role__name="Communication", user_roles__is_active=True
        ).distinct()

        for user in communication_users:
            NotificationServiceBase.notify_user(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                event=event,
                video_request=video_request,
                link=link,
                send_email=send_email,
            )
