from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError


class ThereIsIntentValidator(object):

    def __call__(self, attrs):
        if attrs.get('intent') not in attrs.get('repository').intents:
            raise ValidationError(_(
                'Intent MUST match existing intents for training.'
            ))


class ThereIsEntityValidator(object):

    def __call__(self, attrs):
        entities = attrs.get('entities')
        repository = attrs.get('repository')

        if entities:
            entities_list = list(set(
                map(lambda x: x.get('entity'), attrs.get('entities'))))
            repository_entities_list = repository.entities.filter(
                value__in=entities_list)

            if len(entities_list) != len(repository_entities_list):
                raise ValidationError({'entities': _(
                    'Entities MUST match existing entities for training.'
                )})
