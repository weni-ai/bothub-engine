from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from .models import RepositoryUpdate


@staff_member_required
def download_bot_data(self, update_id):  # pragma: no cover
    update = get_object_or_404(RepositoryUpdate, id=update_id)
    if not update.trained_at:
        raise ValidationError('Update #{} not trained at.'.format(update.id))
    response = HttpResponse(
        update.get_bot_data(),
        content_type='application/gzip')
    response['Content-Disposition'] = 'inline; filename={}.tar.gz'.format(
        update.id)
    return response
