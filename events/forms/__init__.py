"""Package de formulaires pour les événements.

Ce package regroupe tous les formulaires liés aux événements,
organisés par domaine fonctionnel (SRP - Single Responsibility Principle).

Usage:
    from events.forms import EventForm, EventImageForm
    # ou
    from events.forms.event import EventForm
    from events.forms.media import EventImageForm
"""

from events.forms.comment import EventCommentForm
from events.forms.event import EventForm
from events.forms.media import EventDocumentForm, EventImageForm
from events.forms.recurrence import EventRecurrenceForm
from events.forms.settings import EventSettingsForm, VideoNotificationSettingsForm

__all__ = [
    "EventForm",
    "EventImageForm",
    "EventDocumentForm",
    "EventCommentForm",
    "EventRecurrenceForm",
    "EventSettingsForm",
    "VideoNotificationSettingsForm",
]
