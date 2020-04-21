from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from bothub.common.models import Repository


def repository_shortcut(self, **kwargs):  # pragma: no cover
    repository = get_object_or_404(Repository, **kwargs)
    if "repository_version" in self.GET:
        version = self.GET.get("repository_version")
    else:
        version = repository.current_version().repository_version.pk
    response = redirect(f"/v2/repository/info/{repository.uuid}/{version}/")
    return response
