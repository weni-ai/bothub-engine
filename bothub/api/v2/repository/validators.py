import re

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.exceptions import ValidationError


class CanContributeInRepositoryExampleValidator(object):
    def __call__(self, value):
        repository = value.repository_update.repository
        user_authorization = repository.get_user_authorization(self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class CanContributeInRepositoryTranslatedExampleValidator(object):
    def __call__(self, value):
        repository = value.original_example.repository_update.repository
        user_authorization = repository.get_user_authorization(self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class CanUseNameVersionValidator(object):
    def __call__(self, value):
        if re.search("[^A-Za-z0-9]+", value):
            raise ValidationError(_("Only letters and numbers allowed"))


class CanContributeInRepositoryValidator(object):
    def __call__(self, value):
        user_authorization = value.get_user_authorization(self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class CanContributeInRepositoryVersionValidator(object):
    def __call__(self, value):
        user_authorization = value.repository.get_user_authorization(self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class ExampleWithIntentOrEntityValidator(object):
    def __call__(self, attrs):
        intent = attrs.get("intent")
        entities = attrs.get("entities")

        if not intent and not entities:
            raise ValidationError(_("Define a intent or one entity"))


class EntityNotEqualLabelValidator(object):
    def __call__(self, attrs):
        entity = attrs.get("entity")
        label = attrs.get("label")

        if entity == label:
            raise ValidationError(
                {"label": _("Label name can't be equal to entity name")}
            )


class APIExceptionCustom(APIException):
    """Readers error class"""

    def __init__(self, detail):
        APIException.__init__(self, detail)
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = detail
