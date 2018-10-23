from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from bothub.common.models import Repository


def repository_shortcut(self, **kwargs):
    repository = get_object_or_404(Repository, **kwargs)
    return redirect('repository-detail', uuid=repository.uuid)
