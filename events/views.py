"""Vues pour l'app events.

Ce fichier est maintenu pour la compatibilité ascendante.
Toutes les vues sont maintenant organisées dans le package events/views/.

Pour importer une vue, utilisez :
    from events.views import EventListView
    
Ou directement depuis le sous-module :
    from events.views.base import EventListView
"""

# Ré-exporte toutes les vues depuis le nouveau package
# pour maintenir la compatibilité avec les imports existants
from events.views import *  # noqa: F401, F403
