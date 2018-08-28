from rest_framework import serializers

from bothub.common.models import RepositoryEntity
from bothub.common.models import RepositoryEntityLabel


class ModelMultipleChoiceField(serializers.ManyRelatedField):
    pass


class TextField(serializers.CharField):
    pass


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('trim_whitespace', None)
        super().__init__(trim_whitespace=False, **kwargs)


class EntityText(serializers.CharField):
    pass


class EntityValueField(serializers.CharField):
    def __init__(self, *args, validators=[], **kwargs):
        kwargs.pop('max_length', 0)
        kwargs.pop('help_text', '')

        value_field = RepositoryEntity._meta.get_field('value')

        super().__init__(
            *args,
            max_length=value_field.max_length,
            validators=(validators + value_field.validators),
            **kwargs)

    def to_representation(self, obj):
        return obj.value


class LabelValueField(serializers.CharField):
    def __init__(self, *args, validators=[], **kwargs):
        kwargs.pop('max_length', 0)
        kwargs.pop('help_text', '')

        value_field = RepositoryEntityLabel._meta.get_field('value')

        super().__init__(
            *args,
            max_length=value_field.max_length,
            validators=(validators + value_field.validators),
            **kwargs)

    def to_representation(self, obj):
        return obj.value
