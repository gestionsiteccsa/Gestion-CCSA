from django.shortcuts import render
from django.utils import timezone
from leave.models import LeaveCalendar


def index(request):
    context = {}

    # Récupérer le calendrier de congés actif (même à venir)
    if request.user.is_authenticated:
        active_calendar = LeaveCalendar.objects.filter(
            is_active=True
        ).order_by("-start_date").first()
        context['active_leave_calendar'] = active_calendar

    return render(request, "home/index.html", context)


def changelog(request):
    """Affiche la page du changelog."""
    return render(request, "home/changelog.html")
