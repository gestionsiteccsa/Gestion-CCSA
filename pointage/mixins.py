"""Mixins pour l'app pointage."""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AccueilRequiredMixin(UserPassesTestMixin):
    """Mixin qui vérifie que l'utilisateur a le rôle 'Accueil' (insensible à la casse)."""

    def test_func(self):
        """Vérifie si l'utilisateur a le rôle Accueil."""
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Vérification insensible à la casse avec __iexact
        return user.user_roles.filter(role__name__iexact="accueil", is_active=True).exists()

    def handle_no_permission(self):
        """Gère le cas où l'utilisateur n'a pas la permission."""
        raise PermissionDenied("Vous devez avoir le rôle Accueil pour accéder à cette page.")
