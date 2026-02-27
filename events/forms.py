"""Formulaires pour l'app events.

⚠️  DEPRECATED: Ce module est déprécié.
Utilisez le package `events.forms` à la place.

Exemple:
    # Ancien (déprécié)
    from events.forms import EventForm
    
    # Nouveau (recommandé)
    from events.forms.event import EventForm
    # ou
    from events.forms import EventForm
"""

import warnings

# Émettre un avertissement de dépréciation
warnings.warn(
    "Le module events.forms monolithique est déprécié. "
    "Utilisez le package events.forms à la place. "
    "Les imports restent compatibles mais la structure a été refactorisée.",
    DeprecationWarning,
    stacklevel=2,
)

# Imports pour compatibilité rétrograde
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
