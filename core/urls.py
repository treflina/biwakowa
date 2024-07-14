from django.urls import path

from . import views as core_views

urlpatterns = [
    path("android-chrome-96x96.png", core_views.favicon_file),
    path("android-chrome-192x192.png", core_views.favicon_file),
    path("android-chrome-512x512.png", core_views.favicon_file),
    path("apple-touch-icon.png", core_views.favicon_file),
    path("browserconfig.xml", core_views.favicon_file),
    path("favicon-16x16.png", core_views.favicon_file),
    path("favicon-32x32.png", core_views.favicon_file),
    path("favicon.ico", core_views.favicon_file),
    path("mstile-150x150.png", core_views.favicon_file),
    path("safari-pinned-tab.svg", core_views.favicon_file),
]
