"""Vues pour le pointage journalier."""

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from pointage.forms import DateSelectionForm
from pointage.mixins import AccueilRequiredMixin
from pointage.models import DailyTracking, SectionType, TrackingHistory


class DailyTrackingView(LoginRequiredMixin, AccueilRequiredMixin, TemplateView):
    """Vue pour afficher et gérer le pointage journalier."""

    template_name = "pointage/daily_tracking.html"

    def get_context_data(self, **kwargs):
        """Ajoute les données nécessaires au contexte."""
        context = super().get_context_data(**kwargs)

        # Récupérer la date sélectionnée (défaut: aujourd'hui)
        selected_date_str = self.kwargs.get("date")
        if selected_date_str:
            selected_date = date.fromisoformat(selected_date_str)
        else:
            selected_date = date.today()

        # Vérifier la limite de rétroactivité (30 jours)
        today = date.today()
        min_date = today - timedelta(days=30)
        if selected_date < min_date:
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied(
                "Vous ne pouvez pas pointer pour une date antérieure à 30 jours."
            )

        # Récupérer toutes les sections actives
        sections = SectionType.objects.active().order_by("order", "name")

        # Récupérer ou créer les pointages pour chaque section
        tracking_data = {}
        for section in sections:
            tracking, created = DailyTracking.objects.get_or_create_tracking(
                date=selected_date,
                section=section,
                defaults={
                    "created_by": self.request.user,
                    "updated_by": self.request.user,
                },
            )
            tracking_data[section.id] = {
                "tracking": tracking,
                "count": tracking.count,
            }

        context.update(
            {
                "sections": sections,
                "selected_date": selected_date,
                "tracking_data": tracking_data,
                "min_date": min_date,
                "max_date": today,
                "date_form": DateSelectionForm(initial={"date": selected_date}),
            }
        )

        return context


class UpdateTrackingView(LoginRequiredMixin, AccueilRequiredMixin, View):
    """Vue pour mettre à jour un pointage via AJAX."""

    def post(self, request, pk):
        """Met à jour le compteur d'un pointage."""
        import json

        tracking = get_object_or_404(DailyTracking, pk=pk)

        # Vérifier que c'est une requête AJAX
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"error": "Requête invalide"},
                status=400,
            )

        # Parser les données JSON
        try:
            data = json.loads(request.body)

            # Vérifier si on a une valeur directe ou un delta
            if "value" in data:
                # Saisie directe : définir une valeur absolue
                new_value = int(data.get("value", 0))
                if new_value < 0:
                    return JsonResponse(
                        {"error": "La valeur ne peut pas être négative"},
                        status=400,
                    )

                # Calculer le delta nécessaire pour atteindre la valeur souhaitée
                delta = new_value - tracking.count
                if delta != 0:
                    success = tracking.update_count(delta, request.user)
                    if not success:
                        return JsonResponse(
                            {"error": "Le compteur ne peut pas être négatif"},
                            status=400,
                        )
            else:
                # Incrémentation/décrémentation avec delta
                delta = int(data.get("delta", 0))

                # Vérifier que delta est entre -5 et 5
                if delta < -5 or delta > 5:
                    return JsonResponse(
                        {"error": "Le delta doit être compris entre -5 et 5"},
                        status=400,
                    )

                # Mettre à jour le compteur
                success = tracking.update_count(delta, request.user)
                if not success:
                    return JsonResponse(
                        {"error": "Le compteur ne peut pas être négatif"},
                        status=400,
                    )
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse(
                {"error": "Données invalides"},
                status=400,
            )

        return JsonResponse(
            {
                "success": True,
                "new_count": tracking.count,
                "tracking_id": tracking.id,
            }
        )


class RetroactiveTrackingView(LoginRequiredMixin, AccueilRequiredMixin, TemplateView):
    """Vue pour saisir le pointage rétroactivement via formulaire."""

    template_name = "pointage/retroactive_tracking.html"

    def get_context_data(self, **kwargs):
        """Ajoute les données nécessaires au contexte."""
        context = super().get_context_data(**kwargs)

        # Récupérer la date sélectionnée depuis GET ou utiliser hier par défaut
        selected_date_str = self.request.GET.get("date")
        if selected_date_str:
            try:
                selected_date = date.fromisoformat(selected_date_str)
            except ValueError:
                selected_date = date.today() - timedelta(days=1)
        else:
            # Par défaut : hier
            selected_date = date.today() - timedelta(days=1)

        # Vérifier la limite de rétroactivité (30 jours)
        today = date.today()
        min_date = today - timedelta(days=30)

        # Récupérer toutes les sections actives
        sections = SectionType.objects.active().order_by("order", "name")

        # Récupérer ou créer les pointages pour chaque section
        tracking_data = {}
        for section in sections:
            tracking, created = DailyTracking.objects.get_or_create_tracking(
                date=selected_date,
                section=section,
                defaults={
                    "created_by": self.request.user,
                    "updated_by": self.request.user,
                },
            )
            tracking_data[section.id] = {
                "tracking": tracking,
                "count": tracking.count,
            }

        context.update(
            {
                "sections": sections,
                "selected_date": selected_date,
                "tracking_data": tracking_data,
                "min_date": min_date,
                "max_date": today,
            }
        )

        return context
