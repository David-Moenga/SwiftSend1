from django.contrib import admin
from django.urls import include, path

from .views import health_check


urlpatterns = [
    path("", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("transfers.urls")),
]
