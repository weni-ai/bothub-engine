from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata
from rest_framework import serializers

from .fields import ModelMultipleChoiceField
from .fields import TextField
from .fields import PasswordField


class Metadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if isinstance(field, ModelMultipleChoiceField):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_text(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]
        if hasattr(field, 'style'):
            field_info['style'] = field.style
        return field_info


Metadata.label_lookup[ModelMultipleChoiceField] = 'multiple choice'
Metadata.label_lookup[TextField] = 'text'
Metadata.label_lookup[PasswordField] = 'password'
Metadata.label_lookup[serializers.HiddenField] = 'hidden'
