from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as rest_framework_authtoken_views

urlpatterns = [
    path('auth/', include([
        path('login/', rest_framework_authtoken_views.obtain_auth_token),
    ])),
    path('api/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
