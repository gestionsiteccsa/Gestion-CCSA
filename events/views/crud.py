"""Views pour le CRUD des événements."""

import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from accounts.services import NotificationService
from events.forms import EventForm
from events.models import Event, EventChangeLog

logger = logging.getLogger("events")


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
        context["submit_label"] = "Créer l'événement"
        return context

    def post(self, request, *args, **kwargs):
        """Gère les champs date/time séparés."""
        logger.info(f"POST request received for event creation by user {request.user}")
        logger.debug(f"POST data: {request.POST.dict()}")

        # Reconstruire les datetime à partir des champs séparés
        post_data = request.POST.copy()

        start_date = post_data.get("start_date")
        start_time = post_data.get("start_time")
        all_day = post_data.get("all_day") == "on"

        logger.debug(
            f"Parsed dates - start_date: {start_date}, start_time: {start_time}, all_day: {all_day}"
        )

        if start_date:
            if all_day:
                # Mode journée entière : 00:00
                post_data["start_datetime"] = f"{start_date}T00:00"
                logger.debug(f"Set start_datetime (all_day): {post_data['start_datetime']}")
            elif start_time:
                try:
                    dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                    post_data["start_datetime"] = dt.strftime("%Y-%m-%dT%H:%M")
                    logger.debug(f"Set start_datetime: {post_data['start_datetime']}")
                except ValueError as e:
                    logger.error(f"Error parsing start datetime: {e}")
                    pass

        end_date = post_data.get("end_date")
        end_time = post_data.get("end_time")

        logger.debug(f"Parsed end dates - end_date: {end_date}, end_time: {end_time}")

        if end_date:
            if all_day:
                # Mode journée entière : 23:59
                post_data["end_datetime"] = f"{end_date}T23:59"
                logger.debug(f"Set end_datetime (all_day): {post_data['end_datetime']}")
            elif end_time:
                try:
                    dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
                    post_data["end_datetime"] = dt.strftime("%Y-%m-%dT%H:%M")
                    logger.debug(f"Set end_datetime: {post_data['end_datetime']}")
                except ValueError as e:
                    logger.error(f"Error parsing end datetime: {e}")
                    pass

        request.POST = post_data
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Sauvegarde l'événement et logue les changements."""
        logger.info(f"Form is valid. Creating event with title: {form.cleaned_data.get('title')}")

        try:
            with transaction.atomic():
                # Définir le créateur
                form.instance.created_by = self.request.user
                logger.debug(f"Set created_by to: {self.request.user}")

                # Sauvegarder l'événement sans commit pour pouvoir sauvegarder les M2M après
                self.object = form.save(commit=False)
                logger.debug(f"Saving event object (commit=False)")
                self.object.save()
                logger.info(
                    f"Event saved successfully with ID: {self.object.id}, slug: {self.object.slug}"
                )

                # Sauvegarder les relations many-to-many
                logger.debug(f"Saving M2M relations (sectors)")
                form.save_m2m()

                # Créer un log de création
                EventChangeLog.objects.create(
                    event=self.object,
                    changed_by=self.request.user,
                    field_name="création",
                    old_value="",
                    new_value="Événement créé",
                )
                logger.debug(f"Created EventChangeLog for event {self.object.id}")

                # Envoyer une notification à l'équipe Communication
                logger.debug(f"Sending notification to communication team")
                NotificationService.notify_event_created(self.object, self.request.user)

                messages.success(self.request, "L'événement a été créé avec succès.")
                logger.info(
                    f"Event creation completed successfully. Redirecting to: {self.get_success_url()}"
                )
                return redirect(self.get_success_url())
        except Exception as e:
            logger.exception(f"Error creating event: {e}")
            messages.error(self.request, f"Erreur lors de la création de l'événement: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Log form errors when validation fails."""
        logger.error(f"Form validation failed for event creation")
        logger.error(f"Form errors: {form.errors}")
        logger.error(f"Non-field errors: {form.non_field_errors()}")
        logger.debug(f"Cleaned data: {form.cleaned_data}")

        # Add specific error messages for common issues
        if "start_datetime" in form.errors:
            messages.error(self.request, "Erreur: La date et heure de début sont invalides.")
        if "sectors" in form.errors:
            messages.error(self.request, "Erreur: Veuillez sélectionner au moins un secteur.")
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        return super().form_invalid(form)

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
        context["submit_label"] = "Enregistrer les modifications"
        context["existing_images"] = self.object.images.all()
        return context

    def post(self, request, *args, **kwargs):
        """Gère les champs date/time séparés."""
        # Reconstruire les datetime à partir des champs séparés
        post_data = request.POST.copy()

        start_date = post_data.get("start_date")
        start_time = post_data.get("start_time")
        all_day = post_data.get("all_day") == "on"

        if start_date:
            if all_day:
                # Mode journée entière : 00:00
                post_data["start_datetime"] = f"{start_date}T00:00"
            elif start_time:
                try:
                    dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                    post_data["start_datetime"] = dt.strftime("%Y-%m-%dT%H:%M")
                except ValueError:
                    pass

        end_date = post_data.get("end_date")
        end_time = post_data.get("end_time")

        if end_date:
            if all_day:
                # Mode journée entière : 23:59
                post_data["end_datetime"] = f"{end_date}T23:59"
            elif end_time:
                try:
                    dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
                    post_data["end_datetime"] = dt.strftime("%Y-%m-%dT%H:%M")
                except ValueError:
                    pass

        request.POST = post_data
        return super().post(request, *args, **kwargs)

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

            # Sauvegarder sans commit pour pouvoir sauvegarder les M2M après
            self.object = form.save(commit=False)
            self.object.save()

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
            return redirect(self.get_success_url())

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
