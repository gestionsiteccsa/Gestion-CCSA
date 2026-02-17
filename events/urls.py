"""URLs pour l'app events."""

from django.urls import path

from events import views

app_name = "events"

urlpatterns = [
    # Liste et calendrier
    path("", views.EventListView.as_view(), name="event_list"),
    path("calendrier/", views.EventCalendarView.as_view(), name="event_calendar"),
    path(
        "calendrier/<int:year>/<int:month>/",
        views.EventCalendarView.as_view(),
        name="event_calendar_month",
    ),
    # Validation par l'équipe Communication (DOIT ÊTRE AVANT les URLs avec slug)
    path(
        "communication/dashboard/",
        views.CommunicationDashboardView.as_view(),
        name="communication_dashboard",
    ),
    path(
        "parametres/email-video/",
        views.VideoEmailSettingsView.as_view(),
        name="video_email_settings",
    ),
    path(
        "administration/parametres/",
        views.EventSettingsView.as_view(),
        name="event_settings",
    ),
    path(
        "validation/",
        views.EventValidationListView.as_view(),
        name="event_validation_list",
    ),
    path(
        "validation/<slug:slug>/",
        views.EventValidationDetailView.as_view(),
        name="event_validation",
    ),
    path(
        "validation/<slug:slug>/envoyer-demande-video/",
        views.send_video_request,
        name="send_video_request",
    ),
    # Confirmation par le caméraman (lien public sécurisé par token)
    path(
        "validation/confirmation/<uuid:token>/",
        views.confirm_video_request,
        name="confirm_video_request",
    ),
    path(
        "validation/refus/<uuid:token>/",
        views.refuse_video_request,
        name="refuse_video_request",
    ),
    path(
        "<slug:slug>/download-ics/",
        views.download_ics,
        name="download_ics",
    ),
    # CRUD
    path("creer/", views.EventCreateView.as_view(), name="event_create"),
    path("<slug:slug>/", views.EventDetailView.as_view(), name="event_detail"),
    path("<slug:slug>/modifier/", views.EventUpdateView.as_view(), name="event_update"),
    path("<slug:slug>/supprimer/", views.EventDeleteView.as_view(), name="event_delete"),
    # Gestion des images
    path(
        "<slug:slug>/images/reorder/",
        views.reorder_images,
        name="reorder_images",
    ),
    path(
        "<slug:slug>/images/<int:image_id>/delete/",
        views.delete_image,
        name="delete_image",
    ),
    # Duplication d'événement
    path(
        "<slug:slug>/dupliquer/",
        views.EventDuplicateView.as_view(),
        name="event_duplicate",
    ),
    # Gestion des documents
    path(
        "<slug:slug>/documents/<int:document_id>/delete/",
        views.delete_document,
        name="delete_document",
    ),
]
