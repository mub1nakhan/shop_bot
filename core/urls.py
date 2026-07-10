"""
Minimal URL configuration.

This project has NO public-facing website. The only reason Django's URL
routing exists here is to serve the Admin panel (and media files in DEBUG).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Jalyuzi/Parda — Boshqaruv paneli"
admin.site.site_title = "Blinds Admin"
admin.site.index_title = "Katalogni boshqarish"