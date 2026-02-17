"""Views pour le tableau de bord de l'équipe Communication."""

from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from events.mixins import CommunicationRequiredMixin
from events.models import Event, EventValidation, Sector


class CommunicationDashboardView(CommunicationRequiredMixin, TemplateView):
    """Vue tableau de bord pour l'équipe Communication avec comparaisons temporelles."""

    template_name = "events/communication_dashboard.html"

    def get_context_data(self, **kwargs):
        """Prépare les données statistiques pour le tableau de bord."""
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        today = now.date()

        # ===== PARAMÈTRES DE FILTRAGE =====

        # Année de référence (par défaut: année en cours)
        selected_year = self.request.GET.get("year", today.year)
        try:
            selected_year = int(selected_year)
            # Validation de plage (1900-2100)
            if not (1900 <= selected_year <= 2100):
                selected_year = today.year
                messages.warning(self.request, "Année invalide. Utilisation de l'année en cours.")
        except (ValueError, TypeError):
            selected_year = today.year

        # Mode de comparaison
        compare_mode = self.request.GET.get(
            "compare_mode", "none"
        )  # none, previous_year, ytd, custom

        # Années de comparaison (pour mode custom)
        compare_years = self.request.GET.getlist("compare_years")
        compare_years = [int(y) for y in compare_years if y.isdigit()]

        # Type de période (year, quarter, month, custom)
        period_type = self.request.GET.get("period_type", "year")

        # Dates personnalisées
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        # Trimestre ou mois sélectionné
        selected_quarter = self.request.GET.get("quarter")
        selected_month = self.request.GET.get("month")

        # Métriques à afficher
        selected_metrics = self.request.GET.getlist(
            "metrics", ["total", "validated", "pending", "sectors", "cities", "creators"]
        )

        # ===== CALCUL DES PÉRIODES =====

        # Déterminer la période de référence avec validation
        if period_type == "custom" and date_from and date_to:
            try:
                ref_start = datetime.strptime(date_from, "%Y-%m-%d").date()
                ref_end = datetime.strptime(date_to, "%Y-%m-%d").date()

                # Validation: date de fin doit être après date de début
                if ref_end < ref_start:
                    ref_end = ref_start
                    messages.warning(
                        self.request, "La date de fin doit être après la date de début."
                    )

                # Validation: période max 2 ans pour éviter les requêtes trop lourdes
                if (ref_end - ref_start).days > 730:
                    ref_end = ref_start + timedelta(days=730)
                    messages.warning(self.request, "La période est limitée à 2 ans.")
            except ValueError:
                # Si dates invalides, utiliser l'année en cours
                messages.error(
                    self.request, "Format de date invalide. Utilisation de l'année en cours."
                )
                ref_start = date(selected_year, 1, 1)
                ref_end = date(selected_year, 12, 31)
        elif period_type == "quarter" and selected_quarter:
            quarter = int(selected_quarter)
            ref_start = date(selected_year, (quarter - 1) * 3 + 1, 1)
            if quarter == 4:
                ref_end = date(selected_year, 12, 31)
            else:
                ref_end = date(selected_year, quarter * 3, 1) - timedelta(days=1)
        elif period_type == "month" and selected_month:
            month = int(selected_month)
            ref_start = date(selected_year, month, 1)
            if month == 12:
                ref_end = date(selected_year, 12, 31)
            else:
                ref_end = date(selected_year, month + 1, 1) - timedelta(days=1)
        else:  # year
            ref_start = date(selected_year, 1, 1)
            ref_end = date(selected_year, 12, 31)

        # Calculer la période YTD (Year To Date) jusqu'à la même date
        ytd_end = date(
            selected_year, today.month, min(today.day, 28)
        )  # Éviter les problèmes de fin de mois

        # ===== ANNÉES DISPONIBLES =====

        # Récupérer les années disponibles dans la base
        available_years = Event.objects.dates("start_datetime", "year", order="DESC")
        available_years = [d.year for d in available_years]
        if not available_years:
            available_years = [today.year]

        # Ajouter l'année en cours si pas présente
        if today.year not in available_years:
            available_years.insert(0, today.year)

        # ===== STATISTIQUES POUR LA PÉRIODE DE RÉFÉRENCE =====

        ref_stats = self._calculate_period_stats(ref_start, ref_end)

        # ===== STATISTIQUES YTD =====

        ytd_stats = None
        if compare_mode == "ytd":
            ytd_start = date(selected_year, 1, 1)
            ytd_stats = self._calculate_period_stats(ytd_start, ytd_end)

        # ===== STATISTIQUES DE COMPARAISON =====

        comparison_data = []

        if compare_mode == "previous_year":
            # Comparer avec l'année précédente (même période)
            prev_year = selected_year - 1
            prev_start = ref_start.replace(year=prev_year)
            prev_end = ref_end.replace(year=prev_year)
            prev_stats = self._calculate_period_stats(prev_start, prev_end)
            comparison_data.append(
                {"year": prev_year, "label": f"{prev_year}", "stats": prev_stats, "is_ytd": False}
            )

        elif compare_mode == "ytd":
            # Comparer avec l'année précédente en YTD
            prev_year = selected_year - 1
            prev_ytd_end = ytd_end.replace(year=prev_year)
            prev_ytd_stats = self._calculate_period_stats(date(prev_year, 1, 1), prev_ytd_end)
            comparison_data.append(
                {
                    "year": prev_year,
                    "label": f"{prev_year} (YTD)",
                    "stats": prev_ytd_stats,
                    "is_ytd": True,
                }
            )

        elif compare_mode == "custom" and compare_years:
            # Comparer avec plusieurs années
            for year in compare_years:
                if year != selected_year:
                    comp_start = ref_start.replace(year=year)
                    comp_end = ref_end.replace(year=year)
                    comp_stats = self._calculate_period_stats(comp_start, comp_end)
                    comparison_data.append(
                        {"year": year, "label": str(year), "stats": comp_stats, "is_ytd": False}
                    )

        # ===== CALCUL DES ÉVOLUTIONS =====

        if comparison_data:
            primary_comparison = comparison_data[0]  # Première année de comparaison
            evolution = self._calculate_evolution(ref_stats, primary_comparison["stats"])
        else:
            evolution = None

        # ===== DONNÉES POUR GRAPHIQUES COMPARATIFS =====

        # Graphique évolutif : tous les mois de la période
        chart_data = self._prepare_comparison_chart_data(
            selected_year, comparison_data, ref_start, ref_end
        )

        # ===== MISE À JOUR DU CONTEXTE =====

        # Liste des mois pour le select
        months_list = [
            (1, "Janvier"),
            (2, "Février"),
            (3, "Mars"),
            (4, "Avril"),
            (5, "Mai"),
            (6, "Juin"),
            (7, "Juillet"),
            (8, "Août"),
            (9, "Septembre"),
            (10, "Octobre"),
            (11, "Novembre"),
            (12, "Décembre"),
        ]

        context.update(
            {
                # Paramètres
                "selected_year": selected_year,
                "available_years": available_years,
                "compare_mode": compare_mode,
                "compare_years": compare_years,
                "period_type": period_type,
                "selected_quarter": selected_quarter,
                "selected_month": selected_month,
                "date_from": date_from,
                "date_to": date_to,
                "selected_metrics": selected_metrics,
                "months_list": months_list,
                # Périodes
                "ref_start": ref_start,
                "ref_end": ref_end,
                "ytd_end": ytd_end if compare_mode == "ytd" else None,
                "ref_label": self._format_period_label(ref_start, ref_end),
                # Statistiques
                "ref_stats": ref_stats,
                "ytd_stats": ytd_stats,
                "comparison_data": comparison_data,
                "evolution": evolution,
                # Graphiques
                "chart_data": chart_data,
                # Données brutes pour les graphiques
                "sectors_data": ref_stats["sectors_data"],
                "sectors_labels": ref_stats["sectors_labels"],
                "sectors_colors": ref_stats["sectors_colors"],
                "cities_data": ref_stats["cities_data"],
                "cities_labels": ref_stats["cities_labels"],
                "validation_data": ref_stats["validation_data"],
                # Listes
                "recent_events": ref_stats["recent_events"],
                "pending_events": ref_stats["pending_events"],
                "old_pending_events": ref_stats["old_pending_events"],
                "top_creators": ref_stats["top_creators"],
            }
        )

        return context

    def _calculate_period_stats(self, start_date, end_date):
        """Calcule les statistiques pour une période donnée."""

        # Filtrer les événements sur la période
        base_queryset = Event.objects.filter(
            start_datetime__date__gte=start_date, start_datetime__date__lte=end_date
        )

        # Statistiques de base
        total_events = base_queryset.count()
        active_events = base_queryset.filter(is_active=True).count()

        # Événements validés et en attente (optimisé avec select_related)
        validated_events = (
            EventValidation.objects.select_related("event")
            .filter(
                is_validated=True,
                event__start_datetime__date__gte=start_date,
                event__start_datetime__date__lte=end_date,
            )
            .count()
        )

        pending_validation = base_queryset.filter(is_active=True, validation__isnull=True).count()

        total_with_validation = base_queryset.filter(validation__isnull=False).count()
        validation_rate = (
            (validated_events / total_with_validation * 100) if total_with_validation > 0 else 0
        )

        # Répartition par secteur (optimisé - une seule requête)
        sectors_with_counts = Sector.objects.filter(
            is_active=True, events__in=base_queryset.filter(is_active=True)
        ).annotate(event_count=Count("events", distinct=True)).filter(event_count__gt=0).order_by(
            "-event_count"
        )

        sectors_data = list(sectors_with_counts.values_list("event_count", flat=True))
        sectors_labels = list(sectors_with_counts.values_list("name", flat=True))
        sectors_colors = list(sectors_with_counts.values_list("color_code", flat=True))

        # Top villes
        cities_data = []
        cities_labels = []

        top_cities = (
            base_queryset.filter(is_active=True)
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        for city_data in top_cities:
            cities_data.append(city_data["count"])
            cities_labels.append(city_data["city"])

        # Top créateurs
        top_creators = (
            base_queryset.values("created_by__first_name", "created_by__last_name", "created_by__email")
            .annotate(event_count=Count("id"))
            .order_by("-event_count")[:10]
        )

        return {
            "total_events": total_events,
            "active_events": active_events,
            "validated_events": validated_events,
            "pending_validation": pending_validation,
            "validation_rate": round(validation_rate, 1),
            "sectors_data": sectors_data,
            "sectors_labels": sectors_labels,
            "sectors_colors": sectors_colors,
            "cities_data": cities_data,
            "cities_labels": cities_labels,
            "validation_data": [validated_events, pending_validation],
            "recent_events": base_queryset.select_related("created_by")
            .prefetch_related("sectors")
            .order_by("-created_at")[:10],
            "pending_events": base_queryset.filter(is_active=True, validation__isnull=True)
            .select_related("created_by")
            .prefetch_related("sectors")
            .order_by("-created_at")[:10],
            "old_pending_events": base_queryset.filter(
                is_active=True,
                validation__isnull=True,
                created_at__lte=timezone.now() - timedelta(days=7),
            )
            .select_related("created_by")
            .prefetch_related("sectors")
            .order_by("created_at")[:5],
            "top_creators": top_creators,
        }

    def _calculate_evolution(self, current_stats, previous_stats):
        """Calcule les évolutions entre deux périodes."""
        evolution = {}

        metrics = ["total_events", "active_events", "validated_events", "pending_validation"]

        for metric in metrics:
            current = current_stats.get(metric, 0)
            previous = previous_stats.get(metric, 0)

            if previous > 0:
                pct_change = ((current - previous) / previous) * 100
            elif current > 0:
                pct_change = 100
            else:
                pct_change = 0

            evolution[metric] = {
                "current": current,
                "previous": previous,
                "absolute_change": current - previous,
                "percentage_change": round(pct_change, 1),
                "is_increase": current >= previous,
            }

        return evolution

    def _format_period_label(self, start_date, end_date):
        """Formate une période en label lisible."""
        if start_date.year == end_date.year:
            if start_date.month == end_date.month:
                return start_date.strftime("%B %Y")
            elif start_date.month == 1 and end_date.month == 12:
                return str(start_date.year)
            else:
                return f"{start_date.strftime('%b')} - {end_date.strftime('%b %Y')}"
        else:
            return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

    def _prepare_comparison_chart_data(self, selected_year, comparison_data, ref_start, ref_end):
        """Prépare les données pour les graphiques comparatifs.
        
        Optimisation: Utilise une seule requête avec TruncMonth et annotation
        au lieu de N requêtes (une par mois par année).
        """
        from datetime import datetime

        # Collecter toutes les années à traiter
        years_to_process = {selected_year}
        for comp in comparison_data:
            years_to_process.add(comp["year"])

        # Générer tous les mois de la période
        months = []
        current = ref_start.replace(day=1)
        while current <= ref_end:
            months.append(current)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Labels des mois
        labels = [m.strftime("%b %Y") for m in months]

        # Une seule requête pour tous les événements sur toutes les périodes
        # Utilisation de TruncMonth pour grouper par mois
        events_by_month = (
            Event.objects.filter(
                start_datetime__year__in=years_to_process,
                start_datetime__date__gte=date(min(years_to_process), 1, 1),
                start_datetime__date__lte=date(max(years_to_process), 12, 31),
            )
            .annotate(month=TruncMonth("start_datetime"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # Construire un dictionnaire pour un accès rapide: {(annee, mois): count}
        month_counts = {}
        for entry in events_by_month:
            month_key = (entry["month"].year, entry["month"].month)
            month_counts[month_key] = entry["count"]

        # Données pour l'année de référence
        ref_data = []
        for month in months:
            month_key = (month.year, month.month)
            ref_data.append(month_counts.get(month_key, 0))

        # Données pour les années de comparaison
        comparison_datasets = []
        colors = ["#00A86B", "#F59E0B", "#8B5CF6", "#EC4899", "#6B7280"]

        for i, comp in enumerate(comparison_data):
            comp_data = []
            for month in months:
                # Adapter le mois à l'année de comparaison
                month_key = (comp["year"], month.month)
                comp_data.append(month_counts.get(month_key, 0))

            comparison_datasets.append(
                {
                    "label": comp["label"],
                    "data": comp_data,
                    "borderColor": colors[i % len(colors)],
                    "backgroundColor": colors[i % len(colors)] + "20",
                }
            )

        return {"labels": labels, "ref_data": ref_data, "comparison_datasets": comparison_datasets}
