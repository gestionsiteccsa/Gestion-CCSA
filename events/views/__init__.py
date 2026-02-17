"""Package views pour l'app events.

Ce package contient toutes les vues Django pour la gestion des événements,
organisées par domaine fonctionnel.
"""

# Vues de base (liste, détail, calendrier)
from events.views.base import EventCalendarView, EventDetailView, EventListView

# CRUD événements
from events.views.crud import EventCreateView, EventDeleteView, EventUpdateView

# Gestion des médias
from events.views.media import delete_document, delete_image, reorder_images

# Workflow de validation
from events.views.validation import (
    EventValidationDetailView,
    EventValidationListView,
)

# Tableau de bord Communication
from events.views.dashboard import CommunicationDashboardView

# Paramètres
from events.views.settings import EventSettingsView

# Duplication d'événements
from events.views.duplicate import EventDuplicateView

# Workflow vidéo
from events.views.video import (
    VideoEmailSettingsView,
    confirm_video_request,
    download_ics,
    generate_ics_file,
    refuse_video_request,
    send_video_request,
    escape_ics_value,
)

__all__ = [
    # Base views
    "EventListView",
    "EventCalendarView",
    "EventDetailView",
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
