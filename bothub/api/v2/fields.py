from rest_framework import serializers

from bothub.common.models import RepositoryEntity, RepositoryVersionLanguage
from bothub.common.models import RepositoryEntityGroup


class ModelMultipleChoiceField(serializers.ManyRelatedField):
    pass


class TextField(serializers.CharField):
    pass


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.pop("trim_whitespace", None)
        super().__init__(trim_whitespace=False, **kwargs)


class EntityText(serializers.CharField):
    pass


class EntityValueField(serializers.CharField):
    def __init__(self, *args, validators=[], **kwargs):
        kwargs.pop("max_length", 0)
        kwargs.pop("help_text", "")

        value_field = RepositoryEntity._meta.get_field("value")

        super().__init__(
            *args,
            max_length=value_field.max_length,
            validators=(validators + value_field.validators),
            **kwargs
        )

    def to_representation(self, obj):
        return obj.value  # pragma: no cover


class LabelValueField(serializers.CharField):  # pragma: no cover
    def __init__(self, *args, validators=[], **kwargs):
        kwargs.pop("max_length", 0)
        kwargs.pop("help_text", "")

        value_field = RepositoryEntityGroup._meta.get_field("value")

        super().__init__(
            *args,
            max_length=value_field.max_length,
            validators=(validators + value_field.validators),
            **kwargs
        )

    def to_representation(self, obj):
        return obj.value  # pragma: no cover


class RepositoryVersionRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        version = RepositoryVersionLanguage.objects.get(
            pk=int(value.pk)
        ).repository_version.pk
        return version
