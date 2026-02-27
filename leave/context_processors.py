"""Context processors pour l'app leave."""

from django.utils import timezone

from .models import LeaveCalendar


def active_leave_calendar(request):
    """Ajoute l'information sur les calendriers actifs au contexte."""
    context = {"has_active_leave_calendar": False}

    if request.user.is_authenticated:
        # Un calendrier est considéré comme actif s'il est marqué actif
        # (même s'il est à venir)
        has_active = LeaveCalendar.objects.filter(is_active=True).exists()
        context["has_active_leave_calendar"] = has_active

    return context