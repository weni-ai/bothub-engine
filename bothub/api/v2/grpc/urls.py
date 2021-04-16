from django.urls import path

from .views import GRPCListRepositoriesConnectView

urlpatterns = [
    path(
        "repositories/<str:project_uuid>/",
        GRPCListRepositoriesConnectView.as_view(),
        name="list-repositories-connect",
    )
]
