"""URLs pour l'app leave."""

from django.urls import path

from . import views

app_name = "leave"

urlpatterns = [
    # Liste et gestion des calendriers
    path("", views.LeaveCalendarListView.as_view(), name="calendar_list"),
    path(
        "calendrier/creer/",
        views.LeaveCalendarCreateView.as_view(),
        name="calendar_create",
    ),
    path(
        "calendrier/<uuid:pk>/",
        views.LeaveCalendarDetailView.as_view(),
        name="calendar_detail",
    ),
    path(
        "calendrier/<uuid:pk>/modifier/",
        views.LeaveCalendarUpdateView.as_view(),
        name="calendar_update",
    ),
    path(
        "calendrier/<uuid:pk>/supprimer/",
        views.LeaveCalendarDeleteView.as_view(),
        name="calendar_delete",
    ),
    path(
        "calendrier/<uuid:pk>/export/",
        views.LeaveExportExcelView.as_view(),
        name="calendar_export",
    ),
    # Gestion des demandes de congés
    path(
        "calendrier/<uuid:calendar_pk>/poser/",
        views.LeaveRequestCreateView.as_view(),
        name="request_create",
    ),
    path(
        "demande/<uuid:pk>/modifier/",
        views.LeaveRequestUpdateView.as_view(),
        name="request_update",
    ),
    path(
        "demande/<uuid:pk>/supprimer/",
        views.LeaveRequestDeleteView.as_view(),
        name="request_delete",
    ),
    # API pour FullCalendar
    path(
        "api/calendrier/<uuid:pk>/evenements/",
        views.LeaveCalendarEventsAPI.as_view(),
        name="calendar_events_api",
    ),
    # Archives (Accueil uniquement)
    path(
        "archives/",
        views.ArchivedCalendarsView.as_view(),
        name="calendar_archives",
    ),
    # Gestion des congés de l'utilisateur
    path(
        "mes-conges/",
        views.UserLeaveRequestsView.as_view(),
        name="user_requests",
    ),
    path(
        "mes-conges/supprimer/",
        views.BulkDeleteLeaveRequestsView.as_view(),
        name="bulk_delete_requests",
    ),
]
