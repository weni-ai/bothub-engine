from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from bothub.api.v2 import urls as bothub_api_v2_urls
from bothub.api.v2.swagger import CustomOpenAPISchemaGenerator
from bothub.health.views import ping
from bothub.health.views import r200
from bothub.common.views import download_bot_data


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v2.0.30",
        description="Documentation",
        terms_of_service="https://bothub.it/terms",
        contact=openapi.Contact(email="bothub@ilhasoft.com.br"),
        license=openapi.License(name="GPL-3.0"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)

urlpatterns = [
    path("", schema_view.with_ui("swagger")),
    path("v2/", include(bothub_api_v2_urls)),
    path("admin/", admin.site.urls),
    path("ping/", ping, name="ping"),
    path("200/", r200, name="200"),
    path(
        "downloadbotdata/<int:update_id>/", download_bot_data, name="download_bot_data"
    ),
]

if settings.DEBUG:

    def render_template(template_name, **kwargs):
        def wrapper(request):
            from django.shortcuts import render

            return render(request, template_name, kwargs)

        return wrapper

    urlpatterns += [
        path(
            "emails/",
            include(
                [
                    path(
                        "welcome/",
                        render_template(
                            "authentication/emails/welcome.html",
                            name="User",
                            base_url=settings.BASE_URL,
                        ),
                    ),
                    path(
                        "new-role/",
                        render_template(
                            "common/emails/new_role.html",
                            base_url=settings.BASE_URL,
                            responsible_name="User",
                            user_name="Michael",
                            repository_name="Repository 1",
                            repository_url="http://localhost:8080/user/repo1/",
                            new_role="Admin",
                        ),
                    ),
                    path(
                        "new-request/",
                        render_template(
                            "common/emails/new_request.html",
                            base_url=settings.BASE_URL,
                            user_name="Michael",
                            repository_name="Repository 1",
                            text="Lorem ipsum dolor sit amet, consectetur "
                            + "adipiscing elit. Pellentesque tristique dapibus "
                            + "consectetur. Praesent eleifend sit amet nulla sed "
                            + "egestas. Nam ac quam lacus. Pellentesque posuere, "
                            + "nisl nullam.",
                            repository_url="http://localhost:8080/user/repo1/",
                        ),
                    ),
                    path(
                        "request-rejected/",
                        render_template(
                            "common/emails/request_rejected.html",
                            base_url=settings.BASE_URL,
                            repository_name="Repository 1",
                        ),
                    ),
                    path(
                        "request-approved/",
                        render_template(
                            "common/emails/request_approved.html",
                            base_url=settings.BASE_URL,
                            admin_name="User",
                            repository_name="Repository 1",
                            repository_url="http://localhost:8080/user/repo1/",
                        ),
                    ),
                ]
            ),
        )
    ]
