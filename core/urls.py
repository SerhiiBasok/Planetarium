from django.urls import path, include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/planetarium/", include("planetarium.urls", namespace="planetarium")),
    # path("api/user/", include("user.urls", namespace="user")),
]
