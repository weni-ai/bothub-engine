import json

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt

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
    if request.method == "GET":
        obj = get_object_or_404(User, email=email)
        return JsonResponse({
            "id": obj.pk,
            "username": obj.nickname,
            "email": obj.email,
            "firstName": obj.name,
            "lastName": "",
            "enabled": obj.is_active,
            "emailVerified": obj.is_active,
            "attributes": {},
            "roles": [],
            "groups": []
        })
    elif request.method == "POST":
        obj = get_object_or_404(User, nickname=email)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        obj.check_password(raw_password=body.get('password'))
        return JsonResponse({}) if obj else Http404()
