import re
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.exceptions import ValidationError

from bothub.common.models import Organization


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


class IntentValidator(object):
    def __call__(self, value):
        reg = re.compile(r"^[-a-z0-9_]+\Z")
        if not reg.match(value):
            raise ValidationError(
                _(
                    "Enter a valid value consisting of lowercase letters, numbers, "
                    + "underscores or hyphens."
                )
            )

    def set_context(self, serializer):
        self.request = serializer.context.get("request")


class ExampleTextHasLettersValidator(object):
    def __call__(self, value):
        reg = re.compile(r".[a-zA-Z_]")
        if not reg.match(value):
            raise ValidationError(_("Enter a valid value that has letters in it"))


class ExampleTextHasLimitedWordsValidator(object):
    def __call__(self, value):
        count = len(value.split())
        if count > settings.REPOSITORY_EXAMPLE_TEXT_WORDS_LIMIT:
            raise ValidationError(
                _(
                    "Enter a valid value that is in the range of "
                    + str(settings.REPOSITORY_EXAMPLE_TEXT_WORDS_LIMIT)
                    + " words"
                )
            )


class APIExceptionCustom(APIException):
    """Readers error class"""

    def __init__(self, detail):
        APIException.__init__(self, detail)
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = detail
