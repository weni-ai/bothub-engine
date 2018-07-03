from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.documentation import include_docs_urls

from bothub.api.routers import router as bothub_api_routers


urlpatterns = [
    path('api/', include(bothub_api_routers.urls)),
    path('docs/', include_docs_urls(title='API Documentation')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    def render_template(template_name, **kwargs):
        def wrapper(request):
            from django.shortcuts import render
            return render(request, template_name, kwargs)
        return wrapper

    urlpatterns += [
        path('emails/', include([
            path(
                'welcome/',
                render_template(
                    'authentication/emails/welcome.html',
                    name='Douglas')),
        ])),
    ]
