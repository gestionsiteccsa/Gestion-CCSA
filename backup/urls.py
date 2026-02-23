"""URLs pour l'app backup."""

from django.urls import path

from backup import views

app_name = "backup"

urlpatterns = [
    path("", views.backup_dashboard, name="dashboard"),
    path("create/", views.create_backup_ajax, name="create_ajax"),
    path("download/<str:filename>/", views.download_backup, name="download"),
    path("delete/<str:filename>/", views.delete_backup, name="delete"),
    path("config/", views.update_config, name="update_config"),
]
