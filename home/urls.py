from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("changelog/", views.changelog, name="changelog"),
]
