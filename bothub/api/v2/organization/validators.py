from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from bothub.common.models import Organization


class OrganizationNotExistValidator(object):
    def __call__(self, attrs):
        nickname = attrs.get("nickname")

        if Organization.objects.filter(nickname=nickname).count() > 0:
            raise ValidationError(_("This organization nickname already exists"))
