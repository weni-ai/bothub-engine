import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from bothub.authentication.models import User
from bothub.common.models import Repository


def repository_shortcut(self, **kwargs):  # pragma: no cover
    repository = get_object_or_404(Repository, **kwargs)
    if "repository_version" in self.GET:
        version = self.GET.get("repository_version")
    else:
        version = repository.current_version().repository_version.pk
    response = redirect(f"/v2/repository/info/{repository.uuid}/{version}/")
    return response


@csrf_exempt
def check_user_legacy(request, email: str):  # pragma: no cover
    try:
        if settings.SECRET_KEY_CHECK_LEGACY_USER:
            prefix, token = request.headers.get("Authorization").split()
            if (
                prefix.lower() != "bearer"
                or token != settings.SECRET_KEY_CHECK_LEGACY_USER
            ):
                return HttpResponse(status=404)
    except AttributeError:
        return HttpResponse(status=404)

    if request.method == "GET":
        obj = get_object_or_404(User, email__iexact=email)
        return JsonResponse(
            {
                "id": obj.pk,
                "username": obj.nickname.lower(),
                "email": obj.email.lower(),
                "firstName": obj.name,
                "lastName": "",
                "enabled": obj.is_active,
                "emailVerified": False,
                "attributes": {},
                "roles": [],
                "groups": [],
            }
        )
    elif request.method == "POST":
        obj = get_object_or_404(User, nickname__iexact=email)
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        check_password = obj.check_password(raw_password=body.get("password"))
        return JsonResponse({}) if check_password else HttpResponse(status=404)
    return HttpResponse(status=404)
