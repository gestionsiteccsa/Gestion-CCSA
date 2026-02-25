"""Context processors pour l'app accounts."""

from .models import Notification


def notifications(request):
    """Ajoute les notifications au contexte de tous les templates."""
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "recent_notifications": [],
        }

    return {
        "unread_count": Notification.get_unread_count(request.user),
        "notifications": Notification.get_recent_for_user(request.user, limit=5),
    }
