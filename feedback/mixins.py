"""Mixins de permission pour l'app feedback."""

from django.contrib.auth.mixins import UserPassesTestMixin


class IsSupportMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur a le rôle Support."""

    def test_func(self):
        """Vérifie que l'utilisateur a le rôle Support."""
        return self.request.user.user_roles.filter(
            role__name="Support", is_active=True
        ).exists()


class IsOwnerOrSupportMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est propriétaire ou support."""

    def test_func(self):
        """Vérifie que l'utilisateur est propriétaire ou support."""
        if not self.request.user.is_authenticated:
            return False
        ticket = self.get_object()
        is_owner = ticket.created_by == self.request.user
        is_support = self.request.user.user_roles.filter(
            role__name="Support", is_active=True
        ).exists()
        return is_owner or is_support
