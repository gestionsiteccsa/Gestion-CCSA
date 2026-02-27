"""Package de services de notification.

Ce package regroupe tous les services de notification, organisés par domaine
fonctionnel (SRP - Single Responsibility Principle).

Usage:
    from accounts.notifications import EventNotificationService, VideoNotificationService
    # ou
    from accounts.notifications.events import EventNotificationService
    from accounts.notifications.video import VideoNotificationService
"""

from accounts.notifications.base import NotificationServiceBase
from accounts.notifications.events import EventNotificationService
from accounts.notifications.video import VideoNotificationService

__all__ = [
    "NotificationServiceBase",
    "EventNotificationService",
    "VideoNotificationService",
]
