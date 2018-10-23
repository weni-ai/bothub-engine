from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.documentation import include_docs_urls

from bothub.api.v1.routers import router as bothub_api_routers
from bothub.api.v2 import urls as bothub_api_v2_urls
from bothub.health.views import ping
from bothub.health.views import r200
from bothub.common.views import download_bot_data


urlpatterns = [
    path('', include(bothub_api_routers.urls)),
    path('api/', include(bothub_api_routers.urls)),
    path('api/v2/', include(bothub_api_v2_urls)),
    path('docs/', include_docs_urls(title='API Documentation')),
    path('admin/', admin.site.urls),
    path('ping/', ping, name='ping'),
    path('200/', r200, name='200'),
    path(
        'downloadbotdata/<int:update_id>/',
        download_bot_data,
        name='download_bot_data')
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
