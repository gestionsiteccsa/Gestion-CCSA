"""Views pour la gestion des paramètres globaux des événements."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from events.forms import EventSettingsForm
from events.models import EventSettings


class EventSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue pour configurer les paramètres globaux des événements.

    Accessible uniquement aux superadmins.
    """

    model = EventSettings
    form_class = EventSettingsForm
    template_name = "events/event_settings.html"
    success_url = reverse_lazy("events:event_settings")

    def test_func(self):
        """Vérifie que l'utilisateur est superadmin."""
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        """Récupère ou crée les paramètres."""
        return EventSettings.get_settings()

    def form_valid(self, form):
        """Sauvegarde les paramètres avec l'utilisateur qui a modifié."""
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Les paramètres ont été mis à jour avec succès.")
        return super().form_valid(form)
