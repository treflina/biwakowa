from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("search/", search_views.search, name="search"),
    path("webpush/", include('webpush.urls')),
    path(
        "manifest.json",
        TemplateView.as_view(
            template_name="manifest.json", content_type="application/json"
        ),
        name="manifest.json",
    ),
    path(
        "sw.js",
        (
            TemplateView.as_view(
                template_name="sw.js",
                content_type="application/javascript",
            )
        ),
        name="serviceworker",
    ),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon/favicon.ico'))),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("users.urls")),
    path("", include("bookings.urls")),
    path("", include("apartments.urls")),
    # path('i18n/',include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
