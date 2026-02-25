"""URLs pour l'app pointage."""

from django.urls import path

from pointage.views.daily_tracking import (DailyTrackingView,
                                           RetroactiveTrackingView,
                                           UpdateTrackingView)
from pointage.views.section_management import (SectionCreateView,
                                               SectionListView,
                                               SectionToggleView,
                                               SectionUpdateView)
from pointage.views.stats import StatsDashboardView, StatsDataView

app_name = "pointage"

urlpatterns = [
    # Pointage journalier
    path("", DailyTrackingView.as_view(), name="daily_tracking"),
    path(
        "date/<str:date>/",
        DailyTrackingView.as_view(),
        name="daily_tracking_date",
    ),
    path(
        "retroactive/",
        RetroactiveTrackingView.as_view(),
        name="retroactive_tracking",
    ),
    path(
        "update/<int:pk>/",
        UpdateTrackingView.as_view(),
        name="update_tracking",
    ),
    # Gestion des sections
    path("sections/", SectionListView.as_view(), name="section_list"),
    path(
        "sections/create/",
        SectionCreateView.as_view(),
        name="section_create",
    ),
    path(
        "sections/<int:pk>/update/",
        SectionUpdateView.as_view(),
        name="section_update",
    ),
    path(
        "sections/<int:pk>/toggle/",
        SectionToggleView.as_view(),
        name="section_toggle",
    ),
    # Statistiques
    path("stats/", StatsDashboardView.as_view(), name="stats_dashboard"),
    path("stats/data/", StatsDataView.as_view(), name="stats_data"),
]
