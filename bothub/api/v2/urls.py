from django.urls import path, include

from . import views
from .routers import router

from .zeroshot.views import ZeroShotRepositoryAPIView, ZeroShotOptionsTextAPIView, ZeroShotFastPredictAPIView
from bothub.project.views import ProjectAPIView


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
    path(
        "repository/nlp/zeroshot", ZeroShotRepositoryAPIView.as_view(), name="zeroshot"
    ),
    path(
        "repository/nlp/zeroshot/options",
        ZeroShotOptionsTextAPIView.as_view(),
        name="zeroshot-options",
    ),
    path("project", ProjectAPIView.as_view(), name="project"),
    path(
        "repository/nlp/zeroshot/zeroshot-fast-predict",
        ZeroShotFastPredictAPIView.as_view(),
        name="zeroshot-fast-prediction"
    )
]
