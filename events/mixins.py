"""Mixins partagés entre les vues events."""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from accounts.models import Role, UserRole


class CommunicationRequiredMixin(UserPassesTestMixin):
    """Mixin vérifiant que l'utilisateur a le rôle Communication."""

    def test_func(self):
        """Vérifie si l'utilisateur a le rôle Communication."""
        if not self.request.user.is_authenticated:
            return False
        try:
            communication_role = Role.objects.get(name="Communication", is_active=True)
            return UserRole.objects.filter(
                user=self.request.user, role=communication_role, is_active=True
            ).exists()
        except Role.DoesNotExist:
            return False

    def handle_no_permission(self):
        """Redirige vers la page de connexion si l'utilisateur n'a pas la permission."""
        if not self.request.user.is_authenticated:
            return redirect("login")
        # Afficher un message d'erreur et rediriger
        from django.contrib import messages

        messages.error(
            self.request,
            "Vous n'avez pas les droits pour accéder à cette page. "
            "Cette section est réservée à l'équipe Communication.",
        )
        return redirect("events:event_list")
