from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryEntityLabel
from bothub.common.models import RepositoryEntity


class DoesIntentExistValidator(object):
    """
    Validator that corresponds to `intent` on a RepositoryValidation field.
    It is applied to avoid RepositoryValidation with not existing intents.
    """
    def __call__(self, value):
        examples = RepositoryExample.objects.filter(intent=value)
        if not examples.exists():
            raise ValidationError({'intent': _(
                'Intent MUST match existing intents for training. '
            )})


class DoesEntityAndLabelExistValidator(object):
    """
    It is applied to avoid RepositoryValidation with not existing entities.
    """
    def __call__(self, attrs):
        label = RepositoryEntityLabel.objects.filter(value=attrs.get('label'))

        entity = RepositoryEntity.objects.filter(
            value=attrs.get('entity'),
        )

        if label.exists():
            entity = entity.filter(label__in=label)

        entities = RepositoryExampleEntity.objects.filter(
            entity__in=entity,
        )

        if not entities.exists():
            raise ValidationError({'entities': _(
                'Entities MUST match existing entities for training. '
            )})


class RepositoryValidationWithIntentOrEntityValidator(object):
    def __call__(self, attrs):
        intent = attrs.get('intent')
        entities = attrs.get('entities')

        if not intent and not entities:
            raise ValidationError(_('Define a intent or one entity'))
