from django.shortcuts import render


def index(request):
    return render(request, "home/index.html")


def changelog(request):
    """Affiche la page du changelog."""
    return render(request, "home/changelog.html")
