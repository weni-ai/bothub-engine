from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryTranslatedExample


class CanContributeInRepositoryValidator(object):
    def __call__(self, value):
        user_authorization = value.get_user_authorization(
            self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(
                _('You can\'t contribute in this repository'))

    def set_context(self, serializer):
        self.request = serializer.context.get('request')


class CanContributeInRepositoryExampleValidator(object):
    def __call__(self, value):
        repository = value.repository_update.repository
        user_authorization = repository.get_user_authorization(
            self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(
                _('You can\'t contribute in this repository'))

    def set_context(self, serializer):
        self.request = serializer.context.get('request')


class CanContributeInRepositoryTranslatedExampleValidator(object):
    def __call__(self, value):
        repository = value.original_example.repository_update.repository
        user_authorization = repository.get_user_authorization(
            self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(
                _('You can\'t contribute in this repository'))

    def set_context(self, serializer):
        self.request = serializer.context.get('request')


class TranslatedExampleEntitiesValidator(object):
    def __call__(self, attrs):
        original_example = attrs.get('original_example')
        entities_valid = RepositoryTranslatedExample.same_entities_validator(
            list(map(lambda x: dict(x), attrs.get('entities'))),
            list(map(lambda x: x.to_dict, original_example.entities.all())))
        if not entities_valid:
            raise ValidationError({'entities': _('Invalid entities')})
