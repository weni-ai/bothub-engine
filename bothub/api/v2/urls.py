from django.urls import path, include

from . import views
from .routers import router

from .zeroshot.views import ZeroShotRepositoryAPIView, ZeroShotOptionsTextAPIView, ZeroShotOptionsAPIView, ZeroShotPredictAPIView


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
        "repository/nlp/zeroshot/options-synonym",
        ZeroShotOptionsTextAPIView.as_view(),
        name="zeroshot-options-synonym",
    ),
    path("repository/nlp/zeroshot/option", ZeroShotOptionsAPIView.as_view(), name="zeroshot-option"),
    path("repository/nlp/zeroshot/zeroshot-predict", ZeroShotPredictAPIView.as_view(), name="zeroshot-predict"),
]
