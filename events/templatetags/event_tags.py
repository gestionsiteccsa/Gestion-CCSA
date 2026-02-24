"""Template tags pour l'app events."""

from django import template
from django.core.cache import cache

from accounts.models import Role, UserRole
from events.models import Event

register = template.Library()


@register.simple_tag(takes_context=True)
def has_communication_role(context):
    """Vérifie si l'utilisateur a le rôle Communication.

    Optimisation: Cache le résultat pendant 5 minutes par utilisateur
    pour éviter les requêtes répétées sur chaque page.
    """
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return False

    # Clé de cache unique par utilisateur
    cache_key = f"user_comm_role_{request.user.id}"
    result = cache.get(cache_key)

    if result is None:
        try:
            communication_role = Role.objects.get(name="Communication", is_active=True)
            result = UserRole.objects.filter(
                user=request.user, role=communication_role, is_active=True
            ).exists()
        except Role.DoesNotExist:
            result = False

        # Mettre en cache pendant 5 minutes (300 secondes)
        cache.set(cache_key, result, 300)

    return result


@register.simple_tag(takes_context=True)
def has_accueil_role(context):
    """Vérifie si l'utilisateur a le rôle 'Accueil' (insensible à la casse).

    Usage dans le template:
        {% has_accueil_role as user_has_accueil_role %}
        {% if user_has_accueil_role %}
            ...
        {% endif %}
    """
    user = context.get("user")
    if not user or not user.is_authenticated:
        return False

    # Vérification insensible à la casse avec __iexact
    return user.user_roles.filter(role__name__iexact="accueil", is_active=True).exists()


@register.simple_tag
def get_pending_validation_count():
    """Retourne le nombre d'événements en attente de validation.

    Optimisation: Cache le résultat pendant 2 minutes pour éviter
    les requêtes COUNT sur chaque page.
    """
    cache_key = "pending_validation_count"
    result = cache.get(cache_key)

    if result is None:
        result = Event.objects.filter(is_active=True, validation__isnull=True).count()
        # Mettre en cache pendant 2 minutes (120 secondes)
        cache.set(cache_key, result, 120)

    return result


@register.filter
def div(value, arg):
    """Divise value par arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def mul(value, arg):
    """Multiplie value par arg."""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0


@register.filter
def sub(value, arg):
    """Soustrait arg de value."""
    try:
        return float(value) - float(arg)
    except ValueError:
        return 0


@register.filter
def get_item(dictionary, key):
    """Récupère une valeur dans un dictionnaire par sa clé."""
    try:
        return dictionary.get(key, "")
    except (AttributeError, TypeError):
        return ""
