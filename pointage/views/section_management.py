"""Vues pour la gestion des sections."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from pointage.forms import SectionTypeForm
from pointage.mixins import AccueilRequiredMixin
from pointage.models import SectionType


class SectionListView(LoginRequiredMixin, AccueilRequiredMixin, ListView):
    """Vue pour lister les sections."""

    model = SectionType
    template_name = "pointage/section_list.html"
    context_object_name = "sections"

    def get_queryset(self):
        """Retourne toutes les sections avec prefetch des pointages."""
        return SectionType.objects.all().order_by("order", "name")


class SectionCreateView(LoginRequiredMixin, AccueilRequiredMixin, CreateView):
    """Vue pour créer une section."""

    model = SectionType
    form_class = SectionTypeForm
    template_name = "pointage/section_form.html"
    success_url = reverse_lazy("pointage:section_list")

    def form_valid(self, form):
        """Ajoute un message de succès."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'La section "{self.object.name}" a été créée avec succès.',
        )
        return response


class SectionUpdateView(LoginRequiredMixin, AccueilRequiredMixin, UpdateView):
    """Vue pour modifier une section."""

    model = SectionType
    form_class = SectionTypeForm
    template_name = "pointage/section_form.html"
    success_url = reverse_lazy("pointage:section_list")

    def form_valid(self, form):
        """Ajoute un message de succès."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'La section "{self.object.name}" a été mise à jour avec succès.',
        )
        return response


class SectionToggleView(LoginRequiredMixin, AccueilRequiredMixin, View):
    """Vue pour activer/désactiver une section."""

    def post(self, request, pk):
        """Active ou désactive une section."""
        from django.shortcuts import get_object_or_404, redirect

        section = get_object_or_404(SectionType, pk=pk)
        section.is_active = not section.is_active
        section.save()

        status = "activée" if section.is_active else "désactivée"
        messages.success(
            request,
            f'La section "{section.name}" a été {status} avec succès.',
        )

        return redirect("pointage:section_list")
