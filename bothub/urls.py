from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from rest_framework.documentation import include_docs_urls

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from bothub.api.v1.routers import router as bothub_api_routers
from bothub.api.v2 import urls as bothub_api_v2_urls
from bothub.health.views import ping
from bothub.health.views import r200
from bothub.common.views import download_bot_data


schema_view = get_schema_view(
   openapi.Info(
      title='API Documentation',
      default_version='v1.0.1',
      description='Documentation',
      terms_of_service='https://www.google.com/policies/terms/',
      contact=openapi.Contact(email='bothub@ilhasoft.com.br'),
      license=openapi.License(name='GPL-3.0'),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/', include(bothub_api_routers.urls)),#Test webapp
    path('v1/', include(bothub_api_routers.urls)),
    path('v2/', include(bothub_api_v2_urls)),
    path('api/v2/', include(bothub_api_v2_urls)),#test webapp
    path('docs/', include_docs_urls(title='API Documentation')),
    path('admin/', admin.site.urls),
    path('ping/', ping, name='ping'),
    path('200/', r200, name='200'),
    path(
        'downloadbotdata/<int:update_id>/',
        download_bot_data,
        name='download_bot_data'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui()),
    path('', schema_view.with_ui('swagger'))
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
            path(
                'new-role/',
                render_template(
                    'common/emails/new_role.html',
                    responsible_name='Douglas',
                    user_name='Michael',
                    repository_name='Repository 1',
                    repository_url='http://localhost:8080/douglas/repo1/',
                    new_role='Admin')),
            path(
                'new-request/',
                render_template(
                    'common/emails/new_request.html',
                    user_name='Michael',
                    repository_name='Repository 1',
                    text='Lorem ipsum dolor sit amet, consectetur ' +
                    'adipiscing elit. Pellentesque tristique dapibus ' +
                    'consectetur. Praesent eleifend sit amet nulla sed ' +
                    'egestas. Nam ac quam lacus. Pellentesque posuere, ' +
                    'nisl nullam.',
                    repository_url='http://localhost:8080/douglas/repo1/')),
            path(
                'request-rejected/',
                render_template(
                    'common/emails/request_rejected.html',
                    repository_name='Repository 1')),
            path(
                'request-approved/',
                render_template(
                    'common/emails/request_approved.html',
                    admin_name='Douglas',
                    repository_name='Repository 1',
                    repository_url='http://localhost:8080/douglas/repo1/')),
        ])),
    ]
