from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import include, path

from url_shortener.models import ShortenedURL


def robots_txt(request):
    """Serve robots.txt to disallow all indexing."""
    content = "User-agent: *\nDisallow: /\n"
    return HttpResponse(content, content_type="text/plain")


def redirect_short_url(request, code):
    """Redirection vers l'URL originale depuis un code court."""
    shortened_url = get_object_or_404(ShortenedURL, code=code)
    return redirect(shortened_url.original_url)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("evenements/", include("events.urls")),
    path("pointage/", include("pointage.urls")),
    path("feedback/", include("feedback.urls")),
    path("backup/", include("backup.urls")),
    path("liens/", include("url_shortener.urls")),
    path("r/<slug:code>/", redirect_short_url, name="short_redirect"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("home.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
