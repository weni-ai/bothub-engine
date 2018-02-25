from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as rest_framework_authtoken_views

from bothub.api.routers import router as bothub_api_routers

urlpatterns = [
    path('auth/', include([
        path('login/', rest_framework_authtoken_views.obtain_auth_token),
    ])),
    path('api/', include(bothub_api_routers.urls)),
    path('admin/', admin.site.urls),
]
