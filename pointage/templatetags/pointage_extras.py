"""Template tags personnalisés pour l'app pointage."""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par sa clé.

    Usage dans le template:
        {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
