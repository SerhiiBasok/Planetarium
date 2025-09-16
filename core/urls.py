from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from core import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/planetarium/", include("planetarium.urls", namespace="planetarium")),
    path("api/user/", include("user.urls", namespace="user")),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
