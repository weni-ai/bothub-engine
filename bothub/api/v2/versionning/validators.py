import re

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryVersion


class VersionNameNotExistValidator(object):
    def __call__(self, attrs):
        repository = attrs.get("repository")
        name = attrs.get("name")

        if name and re.search("[^A-Za-z0-9]+", name):
            raise ValidationError(_("Only letters and numbers allowed"))

        if (
            RepositoryVersion.objects.filter(repository=repository, name=name).count()
            > 0
        ):
            raise ValidationError(_("This Repository already exists"))


class CanUseNameVersionValidator(object):
    def __call__(self, value):
        if re.search("[^A-Za-z0-9]+", value):
            raise ValidationError(_("Only letters and numbers allowed"))
