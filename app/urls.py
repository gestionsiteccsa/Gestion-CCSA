from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def robots_txt(request):
    """Serve robots.txt to disallow all indexing."""
    content = "User-agent: *\nDisallow: /\n"
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("evenements/", include("events.urls")),
    path("backup/", include("backup.urls")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("home.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
