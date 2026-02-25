"""Package views pour l'app events.

Ce package contient toutes les vues Django pour la gestion des événements,
organisées par domaine fonctionnel.
"""

# Vues de base (liste, détail, calendrier, archives)
from events.views.base import (
    EventArchiveView,
    EventCalendarView,
    EventDetailView,
    EventListView,
    MyEventsView,
)

# CRUD événements
from events.views.crud import EventCreateView, EventDeleteView, EventUpdateView

# Tableau de bord Communication
from events.views.dashboard import CommunicationDashboardView

# Duplication d'événements
from events.views.duplicate import EventDuplicateView

# Gestion des médias
from events.views.media import delete_document, delete_image, reorder_images

# Paramètres
from events.views.settings import EventSettingsView

# Workflow de validation
from events.views.validation import EventValidationDetailView, EventValidationListView

# Workflow vidéo
from events.views.video import (
    VideoEmailSettingsView,
    confirm_video_request,
    download_ics,
    escape_ics_value,
    generate_ics_file,
    refuse_video_request,
    send_video_request,
)

__all__ = [
    # Base views
    "EventListView",
    "EventArchiveView",
    "EventCalendarView",
    "EventDetailView",
    "MyEventsView",
    # CRUD views
    "EventCreateView",
    "EventUpdateView",
    "EventDeleteView",
    # Media views
    "reorder_images",
    "delete_image",
    "delete_document",
    # Validation views
    "EventValidationListView",
    "EventValidationDetailView",
    # Dashboard
    "CommunicationDashboardView",
    # Settings
    "EventSettingsView",
    # Duplicate
    "EventDuplicateView",
    # Video workflow
    "VideoEmailSettingsView",
    "send_video_request",
    "confirm_video_request",
    "refuse_video_request",
    "escape_ics_value",
    "generate_ics_file",
    "download_ics",
]
