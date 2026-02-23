"""Vues pour les statistiques de pointage."""

from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views.generic import TemplateView, View

from pointage.mixins import AccueilRequiredMixin
from pointage.models import DailyTracking, SectionType


class StatsDashboardView(LoginRequiredMixin, AccueilRequiredMixin, TemplateView):
    """Vue pour le dashboard de statistiques."""

    template_name = "pointage/stats_dashboard.html"

    def get_context_data(self, **kwargs):
        """Ajoute les données statistiques au contexte."""
        context = super().get_context_data(**kwargs)

        today = date.today()

        # Périodes par défaut
        context.update(
            {
                "periods": [
                    {"key": "day", "label": "Jour", "days": 1},
                    {"key": "week", "label": "Semaine", "days": 7},
                    {"key": "month", "label": "Mois", "days": 30},
                ],
                "sections": SectionType.objects.active(),
            }
        )

        return context


class StatsDataView(LoginRequiredMixin, AccueilRequiredMixin, View):
    """Vue API pour récupérer les données statistiques (JSON)."""

    def get(self, request):
        """Retourne les données statistiques au format JSON."""
        period = request.GET.get("period", "day")
        target_date_str = request.GET.get("date")

        if target_date_str:
            target_date = date.fromisoformat(target_date_str)
        else:
            target_date = date.today()

        # Définir la plage de dates selon la période
        if period == "day":
            start_date = target_date
            end_date = target_date
        elif period == "week":
            start_date = target_date - timedelta(days=6)
            end_date = target_date
        elif period == "month":
            start_date = target_date - timedelta(days=29)
            end_date = target_date
        else:
            return JsonResponse(
                {"error": "Période invalide"},
                status=400,
            )

        # Récupérer les statistiques
        sections = SectionType.objects.active()
        labels = []
        datasets = []

        # Générer les labels (dates)
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime("%d/%m"))
            current_date += timedelta(days=1)

        # Pour chaque section, créer un dataset
        for section in sections:
            data = []
            current_date = start_date

            while current_date <= end_date:
                try:
                    tracking = DailyTracking.objects.get(
                        date=current_date,
                        section=section,
                    )
                    data.append(tracking.count)
                except DailyTracking.DoesNotExist:
                    data.append(0)

                current_date += timedelta(days=1)

            datasets.append(
                {
                    "label": section.name,
                    "data": data,
                    "backgroundColor": section.color
                    + "33",  # Ajoute de la transparence
                    "borderColor": section.color,
                    "borderWidth": 2,
                    "fill": True,
                }
            )

        return JsonResponse(
            {
                "labels": labels,
                "datasets": datasets,
            }
        )
