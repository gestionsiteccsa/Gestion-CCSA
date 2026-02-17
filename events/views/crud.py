"""Views pour le CRUD des événements."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from accounts.services import NotificationService
from events.forms import EventForm
from events.models import Event, EventChangeLog


class EventCreateView(LoginRequiredMixin, CreateView):
    """Vue création d'un événement."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def get_context_data(self, **kwargs):
        """Ajoute le titre au contexte."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Créer un événement"
        return context

    def form_valid(self, form):
        """Sauvegarde l'événement et logue les changements."""
        with transaction.atomic():
            # Définir le créateur
            form.instance.created_by = self.request.user

            # Sauvegarder l'événement sans commit pour pouvoir sauvegarder les M2M après
            self.object = form.save(commit=False)
            self.object.save()

            # Sauvegarder les relations many-to-many
            form.save_m2m()

            # Créer un log de création
            EventChangeLog.objects.create(
                event=self.object,
                changed_by=self.request.user,
                field_name="création",
                old_value="",
                new_value="Événement créé",
            )

            # Envoyer une notification à l'équipe Communication
            NotificationService.notify_event_created(self.object, self.request.user)

            messages.success(self.request, "L'événement a été créé avec succès.")
            return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirige vers le détail de l'événement créé."""
        return self.object.get_absolute_url()


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue modification d'un événement."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    slug_url_kwarg = "slug"

    def test_func(self):
        """Vérifie que l'utilisateur est le créateur de l'événement."""
        event = self.get_object()
        return event.created_by == self.request.user

    def get_context_data(self, **kwargs):
        """Ajoute le titre et l'événement au contexte."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Modifier l'événement"
        context["event"] = self.object
        return context

    def form_valid(self, form):
        """Sauvegarde les modifications et logue les changements."""
        with transaction.atomic():
            # Récupérer l'ancien état
            old_instance = Event.objects.get(pk=self.object.pk)
            old_data = {
                field: getattr(old_instance, field)
                for field in [
                    "title",
                    "description",
                    "location",
                    "start_datetime",
                    "end_datetime",
                ]
            }

            # Sauvegarder
            response = super().form_valid(form)

            # Sauvegarder les relations many-to-many
            form.save_m2m()

            # Détecter les changements
            changes = {}
            for field in old_data:
                old_value = old_data[field]
                new_value = getattr(self.object, field)
                if old_value != new_value:
                    changes[field] = {"old": str(old_value), "new": str(new_value)}

            if changes:
                for field_name, change_data in changes.items():
                    EventChangeLog.objects.create(
                        event=self.object,
                        changed_by=self.request.user,
                        field_name=field_name,
                        old_value=change_data.get("old", ""),
                        new_value=change_data.get("new", ""),
                    )

                # Envoyer une notification à l'équipe Communication
                NotificationService.notify_event_updated(self.object, self.request.user)

            messages.success(self.request, "L'événement a été modifié avec succès.")
            return response

    def get_success_url(self):
        """Redirige vers le détail de l'événement modifié."""
        return self.object.get_absolute_url()


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vue suppression d'un événement."""

    model = Event
    template_name = "events/event_confirm_delete.html"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("events:event_list")

    def test_func(self):
        """Vérifie que l'utilisateur est le créateur de l'événement."""
        event = self.get_object()
        return event.created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        """Supprime l'événement et logue l'action."""
        self.object = self.get_object()

        # Sauvegarder le titre avant suppression
        event_title = self.object.title

        # Log de suppression
        EventChangeLog.objects.create(
            event=self.object,
            changed_by=request.user,
            field_name="suppression",
            old_value="Actif",
            new_value="Supprimé",
        )

        # Envoyer une notification à l'équipe Communication
        NotificationService.notify_event_deleted(event_title, request.user)

        # Suppression logique
        self.object.is_active = False
        self.object.save()

        messages.success(request, "L'événement a été supprimé avec succès.")
        return redirect(self.get_success_url())
