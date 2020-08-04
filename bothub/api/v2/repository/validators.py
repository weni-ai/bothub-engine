from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.exceptions import ValidationError

from bothub.common.models import Organization


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


class CanCreateRepositoryInOrganizationValidator(object):
    def __call__(self, value):
        organization = get_object_or_404(Organization, repository_owner=value)
        user_authorization = organization.get_organization_authorization(
            self.request.user
        )
        if not user_authorization.can_contribute:
            raise PermissionDenied(_("You can't contribute in this organization"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class EntityNotEqualGroupValidator(object):
    def __call__(self, attrs):
        entity = attrs.get("entity")
        group = attrs.get("group")

        if entity == group:
            raise ValidationError(
                {"group": _("Group name can't be equal to entity name")}
            )


class APIExceptionCustom(APIException):
    """Readers error class"""

    def __init__(self, detail):
        APIException.__init__(self, detail)
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = detail
