"""Views pour la duplication d'événements."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from events.forms import EventForm
from events.models import Event, EventChangeLog, EventDocument, EventImage


class EventDuplicateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vue pour dupliquer un événement existant."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def test_func(self):
        """Vérifie que l'utilisateur peut dupliquer cet événement."""
        # Récupérer l'événement source
        source_slug = self.kwargs.get("slug")
        source_event = get_object_or_404(Event, slug=source_slug, is_active=True)

        # Vérifier que l'utilisateur est le créateur ou a le rôle Communication
        if source_event.created_by == self.request.user:
            return True

        # Vérifier le rôle Communication
        from accounts.models import Role, UserRole

        try:
            communication_role = Role.objects.get(name="Communication", is_active=True)
            return UserRole.objects.filter(
                user=self.request.user, role=communication_role, is_active=True
            ).exists()
        except Role.DoesNotExist:
            return False

    def get_initial(self):
        """Pré-remplit le formulaire avec les données de l'événement source."""
        initial = super().get_initial()

        source_slug = self.kwargs.get("slug")
        self.source_event = get_object_or_404(Event, slug=source_slug, is_active=True)

        # Copier les champs de base
        initial["title"] = f"Copie de {self.source_event.title}"
        initial["description"] = self.source_event.description
        initial["location"] = self.source_event.location
        initial["city"] = self.source_event.city

        # Proposer des dates par défaut (7 jours plus tard)
        from django.utils import timezone

        new_start = self.source_event.start_datetime + timedelta(days=7)
        new_end = None
        if self.source_event.end_datetime:
            new_end = self.source_event.end_datetime + timedelta(days=7)

        initial["start_datetime"] = new_start
        initial["end_datetime"] = new_end

        # Copier les secteurs
        initial["sectors"] = list(self.source_event.sectors.all())

        return initial

    def get_context_data(self, **kwargs):
        """Ajoute le contexte spécifique à la duplication."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Dupliquer l'événement"
        context["source_event"] = self.source_event
        context["is_duplicate"] = True
        return context

    def form_valid(self, form):
        """Crée le nouvel événement en copiant les médias."""
        with transaction.atomic():
            # Définir le créateur
            form.instance.created_by = self.request.user
            form.instance.status = "pending"  # Le nouvel événement doit être validé

            # Sauvegarder sans commit pour pouvoir sauvegarder les M2M après
            self.object = form.save(commit=False)
            self.object.save()

            # Sauvegarder les relations many-to-many
            form.save_m2m()

            # Copier les images
            for image in self.source_event.images.all():
                EventImage.objects.create(
                    event=self.object,
                    image=image.image,
                    caption=image.caption,
                    order=image.order,
                )

            # Copier les documents
            for document in self.source_event.documents.all():
                EventDocument.objects.create(
                    event=self.object,
                    file=document.file,
                    title=document.title,
                    description=document.description,
                )

            # Créer un log
            EventChangeLog.objects.create(
                event=self.object,
                changed_by=self.request.user,
                field_name="duplication",
                old_value="",
                new_value=f"Dupliqué depuis: {self.source_event.title}",
            )

            messages.success(
                self.request,
                f"L'événement '{self.object.title}' a été créé par duplication. "
                "Il doit maintenant être validé.",
            )
            return redirect(self.get_success_url())

    def get_success_url(self):
        """Redirige vers le détail du nouvel événement."""
        return self.object.get_absolute_url()
