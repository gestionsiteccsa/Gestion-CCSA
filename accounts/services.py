"""Services pour l'app accounts.

⚠️  DEPRECATED: Ce module est déprécié.
Utilisez le package `accounts.notifications` à la place.

Exemple:
    # Ancien (déprécié)
    from accounts.services import NotificationService
    
    # Nouveau (recommandé)
    from accounts.notifications.events import EventNotificationService
    from accounts.notifications.video import VideoNotificationService
"""

import warnings

# Émettre un avertissement de dépréciation
warnings.warn(
    "Le module accounts.services.NotificationService est déprécié. "
    "Utilisez accounts.notifications.events.EventNotificationService "
    "ou accounts.notifications.video.VideoNotificationService selon le cas. "
    "Les imports restent compatibles mais la structure a été refactorisée.",
    DeprecationWarning,
    stacklevel=2,
)

# Imports pour compatibilité rétrograde
from accounts.notifications.base import NotificationServiceBase
from accounts.notifications.events import EventNotificationService
from accounts.notifications.video import VideoNotificationService


class NotificationService(NotificationServiceBase):
    """Service pour gérer les notifications avec respect des préférences.
    
    ⚠️  DEPRECATED: Cette classe est dépréciée.
    Utilisez EventNotificationService ou VideoNotificationService.
    
    Cette classe est conservée pour la compatibilité rétrograde et délègue
    vers les nouvelles classes spécialisées.
    """

    # Méthodes vidéo - délèguent vers VideoNotificationService
    @staticmethod
    def notify_video_refused(video_request, event):
        """Notifie l'équipe Communication quand un cameraman refuse."""
        return VideoNotificationService.notify_video_refused(video_request, event)

    @staticmethod
    def notify_video_confirmed(video_request, event):
        """Notifie l'équipe Communication quand un cameraman confirme."""
        return VideoNotificationService.notify_video_confirmed(video_request, event)

    @staticmethod
    def notify_video_request_sent(video_request, event, is_relance=False, relance_num=0):
        """Notifie l'équipe Communication quand une demande de tournage est envoyée."""
        return VideoNotificationService.notify_video_request_sent(
            video_request, event, is_relance, relance_num
        )

    # Méthodes événements - délèguent vers EventNotificationService
    @staticmethod
    def notify_event_created(event, created_by):
        """Notifie l'équipe Communication quand un événement est créé."""
        return EventNotificationService.notify_event_created(event, created_by)

    @staticmethod
    def notify_event_updated(event, updated_by):
        """Notifie l'équipe Communication quand un événement est modifié."""
        return EventNotificationService.notify_event_updated(event, updated_by)

    @staticmethod
    def notify_event_deleted(event_title, deleted_by):
        """Notifie l'équipe Communication quand un événement est supprimé."""
        return EventNotificationService.notify_event_deleted(event_title, deleted_by)

    @staticmethod
    def notify_event_commented(comment):
        """Notifie l'équipe Communication et le créateur de l'événement."""
        return EventNotificationService.notify_event_commented(comment)

    @staticmethod
    def notify_event_validated(event, validated_by):
        """Notifie le créateur de l'événement quand il est validé."""
        return EventNotificationService.notify_event_validated(event, validated_by)

    @staticmethod
    def notify_event_rejected(event, rejected_by, reason=""):
        """Notifie le créateur de l'événement quand il est rejeté."""
        return EventNotificationService.notify_event_rejected(event, rejected_by, reason)
