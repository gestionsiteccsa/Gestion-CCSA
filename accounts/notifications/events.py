"""Service de notification pour les événements."""

from django.urls import reverse

from accounts.notifications.base import NotificationServiceBase


class EventNotificationService(NotificationServiceBase):
    """Service de notification spécialisé pour les événements.
    
    Gère toutes les notifications liées au cycle de vie des événements :
    création, modification, suppression, commentaires, validation, rejet.
    """

    @staticmethod
    def notify_event_created(event, created_by):
        """Notifie l'équipe Communication quand un événement est créé."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        EventNotificationService.notify_communication_team(
            notification_type="event_created",
            title=f"Nouvel événement - {event.title}",
            message=(
                f'Un nouvel événement "{event.title}" a été créé par '
                f"{created_by.get_full_name() or created_by.email}."
            ),
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_updated(event, updated_by):
        """Notifie l'équipe Communication quand un événement est modifié."""
        link = reverse("events:event_validation", kwargs={"slug": event.slug})

        EventNotificationService.notify_communication_team(
            notification_type="event_updated",
            title=f"Événement modifié - {event.title}",
            message=(
                f'L\'événement "{event.title}" a été modifié par '
                f"{updated_by.get_full_name() or updated_by.email}."
            ),
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_deleted(event_title, deleted_by):
        """Notifie l'équipe Communication quand un événement est supprimé."""
        link = reverse("events:event_list")

        EventNotificationService.notify_communication_team(
            notification_type="event_deleted",
            title=f"Événement supprimé - {event_title}",
            message=(
                f'L\'événement "{event_title}" a été supprimé par '
                f"{deleted_by.get_full_name() or deleted_by.email}."
            ),
            link=link,
        )

    @staticmethod
    def notify_event_commented(comment):
        """Notifie l'équipe Communication et le créateur de l'événement."""
        event = comment.event
        author = comment.author
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        # Notifier l'équipe Communication
        EventNotificationService.notify_communication_team(
            notification_type="event_commented",
            title=f"Nouveau commentaire - {event.title}",
            message=(
                f"{author.get_full_name() or author.email} a commenté "
                f'l\'événement "{event.title}".'
            ),
            event=event,
            link=link,
        )

        # Notifier le créateur de l'événement (s'il n'est pas l'auteur du commentaire)
        if event.created_by != author:
            EventNotificationService.notify_user(
                user=event.created_by,
                notification_type="event_commented",
                title=f"Nouveau commentaire sur votre événement - {event.title}",
                message=(
                    f"{author.get_full_name() or author.email} a commenté "
                    f'votre événement "{event.title}".'
                ),
                event=event,
                link=link,
            )

    @staticmethod
    def notify_event_validated(event, validated_by):
        """Notifie le créateur de l'événement quand il est validé."""
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        EventNotificationService.notify_user(
            user=event.created_by,
            notification_type="event_validated",
            title=f"Événement validé - {event.title}",
            message=(
                f'Votre événement "{event.title}" a été validé par '
                f"{validated_by.get_full_name() or validated_by.email}."
            ),
            event=event,
            link=link,
        )

        # Notifier aussi l'équipe Communication
        EventNotificationService.notify_communication_team(
            notification_type="event_validated",
            title=f"Événement validé - {event.title}",
            message=(
                f'L\'événement "{event.title}" a été validé par '
                f"{validated_by.get_full_name() or validated_by.email}."
            ),
            event=event,
            link=link,
        )

    @staticmethod
    def notify_event_rejected(event, rejected_by, reason=""):
        """Notifie le créateur de l'événement quand il est rejeté."""
        link = reverse("events:event_detail", kwargs={"slug": event.slug})

        message = (
            f'Votre événement "{event.title}" a été rejeté par '
            f"{rejected_by.get_full_name() or rejected_by.email}."
        )
        if reason:
            message += f"\n\nMotif : {reason}"

        EventNotificationService.notify_user(
            user=event.created_by,
            notification_type="event_rejected",
            title=f"Événement rejeté - {event.title}",
            message=message,
            event=event,
            link=link,
        )

        # Notifier aussi l'équipe Communication
        comm_message = (
            f'L\'événement "{event.title}" a été rejeté par '
            f"{rejected_by.get_full_name() or rejected_by.email}."
        )
        if reason:
            comm_message += f"\n\nMotif : {reason}"

        EventNotificationService.notify_communication_team(
            notification_type="event_rejected",
            title=f"Événement rejeté - {event.title}",
            message=comm_message,
            event=event,
            link=link,
        )
