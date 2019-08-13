from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryTranslatedExample


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
        entities_list = list(map(lambda x: dict(x), attrs.get('entities')))
        original_entities_list = list(map(
            lambda x: x.to_dict,
            original_example.entities.all()))
        entities_valid = RepositoryTranslatedExample.same_entities_validator(
            entities_list,
            original_entities_list)
        if not entities_valid:
            raise ValidationError({'entities': _(
                'Entities need to match from the original content. ' +
                'Entities: {0}. Original entities: {1}.').format(
                    RepositoryTranslatedExample.count_entities(
                        entities_list,
                        to_str=True),
                    RepositoryTranslatedExample.count_entities(
                        original_entities_list,
                        to_str=True),
                )})


class TranslatedExampleLanguageValidator(object):
    def __call__(self, attrs):
        original_example = attrs.get('original_example')
        language = attrs.get('language')
        if original_example.repository_update.language == language:
            raise ValidationError({'language': _(
                'Can\'t translate to the same language')})
