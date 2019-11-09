from collections import OrderedDict

from django.utils.encoding import force_text
from rest_framework.metadata import BaseMetadata
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from bothub.api.v2.fields import PasswordField
from bothub.api.v2.fields import ModelMultipleChoiceField
from bothub.api.v2.fields import TextField
from bothub.api.v2.fields import EntityText


class Metadata(BaseMetadata):
    label_lookup = ClassLookupDict(
        {
            serializers.Field: "field",
            serializers.BooleanField: "boolean",
            serializers.NullBooleanField: "boolean",
            serializers.CharField: "string",
            serializers.URLField: "url",
            serializers.EmailField: "email",
            serializers.RegexField: "regex",
            serializers.SlugField: "slug",
            serializers.IntegerField: "integer",
            serializers.FloatField: "float",
            serializers.DecimalField: "decimal",
            serializers.DateField: "date",
            serializers.DateTimeField: "date",
            serializers.TimeField: "time",
            serializers.ChoiceField: "choice",
            serializers.MultipleChoiceField: "multiple choice",
            serializers.FileField: "file upload",
            serializers.ImageField: "image upload",
            serializers.ListField: "list",
            serializers.DictField: "nested object",
            serializers.Serializer: "nested object",
            serializers.ManyRelatedField: "multiple choice",
            serializers.HiddenField: "hidden",
            PasswordField: "password",
            ModelMultipleChoiceField: "multiple choice",
            TextField: "text",
            EntityText: "entity text",
        }
    )

    def determine_metadata(self, request, view):  # pragma: no cover
        metadata = OrderedDict()
        metadata["name"] = view.get_view_name()
        metadata["description"] = view.get_view_description()
        metadata["renders"] = [
            renderer.media_type for renderer in view.renderer_classes
        ]
        metadata["parses"] = [parser.media_type for parser in view.parser_classes]
        if hasattr(view, "get_serializer"):
            actions = self.determine_actions(request, view)
            if actions:
                metadata["actions"] = actions
        return metadata

    def determine_actions(self, request, view):  # pragma: no cover
        actions = {}
        for method in {"PUT", "POST"} & set(view.allowed_methods):
            serializer = view.get_serializer()
            actions[method] = self.get_serializer_info(serializer)
            view.request = request
        return actions

    def get_serializer_info(self, serializer):  # pragma: no cover
        if hasattr(serializer, "child"):
            serializer = serializer.child
        return OrderedDict(
            [
                (field_name, self.get_field_info(field))
                for field_name, field in serializer.fields.items()
            ]
        )

    def get_field_info(self, field):  # pragma: no cover
        field_info = OrderedDict()
        field_info["type"] = self.label_lookup[field] or "field"
        field_info["required"] = getattr(field, "required", False)

        attrs = [
            "read_only",
            "label",
            "help_text",
            "min_length",
            "max_length",
            "min_value",
            "max_value",
            "style",
        ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != "":
                field_info[attr] = (
                    value
                    if isinstance(value, dict)
                    else force_text(value, strings_only=True)
                )

        if getattr(field, "child", None):
            field_info["child"] = self.get_field_info(field.child)
        elif getattr(field, "fields", None):
            field_info["children"] = self.get_serializer_info(field)

        if not field_info.get("read_only") and hasattr(field, "choices"):
            field_info["choices"] = [
                {
                    "value": choice_value,
                    "display_name": force_text(choice_name, strings_only=True),
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info
