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

        # Calculer le nombre de jours
        num_days = (end_date - start_date).days + 1

        # Récupérer les statistiques
        sections = SectionType.objects.active()
        labels = []
        datasets = []
        section_stats = []

        # Générer les labels (dates)
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime("%d/%m"))
            current_date += timedelta(days=1)

        # Variables pour les stats globales
        total_general = 0
        daily_totals = [0] * num_days

        # Pour chaque section, créer un dataset et calculer les stats
        for section in sections:
            data = []
            current_date = start_date
            section_total = 0
            section_max = 0
            section_min = float("inf")
            section_max_date = None

            day_index = 0
            while current_date <= end_date:
                try:
                    tracking = DailyTracking.objects.get(
                        date=current_date,
                        section=section,
                    )
                    count = tracking.count
                except DailyTracking.DoesNotExist:
                    count = 0

                data.append(count)
                section_total += count
                daily_totals[day_index] += count

                if count > section_max:
                    section_max = count
                    section_max_date = current_date.strftime("%d/%m")

                if count < section_min:
                    section_min = count

                current_date += timedelta(days=1)
                day_index += 1

            total_general += section_total

            # Calculer la moyenne de la section
            section_avg = round(section_total / num_days) if num_days > 0 else 0

            datasets.append(
                {
                    "label": section.name,
                    "data": data,
                    "backgroundColor": section.color + "33",
                    "borderColor": section.color,
                    "borderWidth": 2,
                    "fill": True,
                }
            )

            section_stats.append(
                {
                    "name": section.name,
                    "color": section.color,
                    "total": section_total,
                    "average": section_avg,
                    "max": section_max if section_max > 0 else 0,
                    "min": section_min if section_min != float("inf") else 0,
                    "max_date": section_max_date or "-",
                }
            )

        # Calculer les stats globales
        avg_per_day = round(total_general / num_days) if num_days > 0 else 0

        # Trouver le jour avec le maximum et le minimum
        max_day_value = max(daily_totals) if daily_totals else 0
        min_day_value = min(daily_totals) if daily_totals else 0
        max_day_index = daily_totals.index(max_day_value) if daily_totals else 0
        min_day_index = daily_totals.index(min_day_value) if daily_totals else 0
        max_day_date = labels[max_day_index] if labels else "-"
        min_day_date = labels[min_day_index] if labels else "-"

        # Trouver la section la plus populaire
        top_section = (
            max(section_stats, key=lambda x: x["total"]) if section_stats else None
        )

        # Calculer les stats de la période précédente pour comparaison
        prev_start = start_date - timedelta(days=num_days)
        prev_end = end_date - timedelta(days=num_days)
        prev_total = 0

        current_date = prev_start
        while current_date <= prev_end:
            daily_sum = (
                DailyTracking.objects.filter(date=current_date).aggregate(
                    total=Sum("count")
                )["total"]
                or 0
            )
            prev_total += daily_sum
            current_date += timedelta(days=1)

        # Calculer l'évolution
        evolution = 0
        if prev_total > 0:
            evolution = round(((total_general - prev_total) / prev_total) * 100)

        return JsonResponse(
            {
                "labels": labels,
                "datasets": datasets,
                "stats": {
                    "total_general": total_general,
                    "avg_per_day": avg_per_day,
                    "max_day": {
                        "value": max_day_value,
                        "date": max_day_date,
                    },
                    "min_day": {
                        "value": min_day_value,
                        "date": min_day_date,
                    },
                    "top_section": (
                        {
                            "name": top_section["name"] if top_section else "-",
                            "color": top_section["color"] if top_section else "#ccc",
                            "total": top_section["total"] if top_section else 0,
                        }
                        if top_section
                        else None
                    ),
                    "sections": section_stats,
                    "evolution": evolution,
                    "num_days": num_days,
                },
            }
        )
