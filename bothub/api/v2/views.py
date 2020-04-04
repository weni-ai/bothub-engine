from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from bothub.common.models import Repository


def repository_shortcut(self, **kwargs):  # pragma: no cover
    repository = get_object_or_404(Repository, **kwargs)
    response = redirect("repository-detail", uuid=repository.uuid)
    if "repository_version" in self.GET:
        response[
            "Location"
        ] += f'?repository_version={self.GET.get("repository_version")}'
    return response
