from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required

from bothub.common.models import RepositoryNLPTrain


@staff_member_required
def download_bot_data(self, update_id):  # pragma: no cover
    update = get_object_or_404(RepositoryNLPTrain, pk=update_id)
    if update.bot_data is None or update.bot_data == "":
        raise ValidationError(f"Update #{update.pk} not trained at.")
    response = HttpResponseRedirect(
        update.repositoryversionlanguage.get_bot_data.bot_data
    )
    return response
