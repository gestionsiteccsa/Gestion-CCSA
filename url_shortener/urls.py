"""URLs pour l'app url_shortener."""

from django.urls import path

from . import views

app_name = "url_shortener"

urlpatterns = [
    # Liste des liens de l'utilisateur
    path(
        "",
        views.ShortenedURLListView.as_view(),
        name="list"
    ),
    
    # Création d'un nouveau lien
    path(
        "creer/",
        views.ShortenedURLCreateView.as_view(),
        name="create"
    ),
    
    # Suppression d'un lien
    path(
        "supprimer/<slug:code>/",
        views.ShortenedURLDeleteView.as_view(),
        name="delete"
    ),
    
    # Redirection vers l'URL originale (accessible sans login)
    path(
        "r/<slug:code>/",
        views.ShortenedURLRedirectView.as_view(),
        name="redirect"
    ),
]
