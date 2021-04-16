from django.urls import path, include

from . import views
from .routers import router
from .grpc import urls as grpc_urls


urlpatterns = [
    path(
        "repository-shortcut/<slug:owner__nickname>/<slug:slug>/",
        views.repository_shortcut,
        name="repository-shortcut",
    ),
    path(
        "check-user-legacy/<str:email>/",
        views.check_user_legacy,
        name="check-user-legacy",
    ),
    path("", include(router.urls)),
    path("grpc/", include(grpc_urls)),
]
