from bothub.api.v2.repository.validators import (
    ExampleTextHasLettersValidator,
    ChatGPTTokenLimitValidator
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bothub.common import languages
from bothub.common.models import Repository, QAKnowledgeBase, QAtext
from bothub.common.helpers import ChatGPTTokenText

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class QAKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAKnowledgeBase
        fields = [
            "id",
            "repository",
            "title",
            "description",
            "language_count",
            "user_name",
            "user",
            "last_update",
            "created_at",
        ]
        read_only_fields = ["created_at", "last_update"]

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_name = serializers.SerializerMethodField("get_user_name")
    repository = serializers.PrimaryKeyRelatedField(queryset=Repository.objects)
    description = serializers.SerializerMethodField("get_description")
    language_count = serializers.SerializerMethodField("get_languages_count")

    def get_user_name(self, obj):
        return None if obj.user is None else obj.user.nickname

    def get_description(self, obj):
        return obj.get_text_description()

    def get_languages_count(self, obj):
        return obj.get_languages_count()


class QAtextSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAtext
        fields = [
            "id",
            "text",
            "language",
            "knowledge_base",
            "created_at",
            "last_update",
            "title",
        ]
        read_only_fields = ["created_at", "last_update"]

    text = serializers.CharField(
        required=False, validators=[ExampleTextHasLettersValidator(), ChatGPTTokenLimitValidator()]
    )
    knowledge_base = serializers.PrimaryKeyRelatedField(
        queryset=QAKnowledgeBase.objects
    )
    language = serializers.ChoiceField(languages.LANGUAGE_CHOICES, required=True)
    title = serializers.SerializerMethodField("get_title")

    def get_title(self, obj):
        return obj.get_title()

    def validate_gpt_tokens(self):
        value = self.instance.text
        validator = ChatGPTTokenText()
        count, chunks = validator.count_tokens(value)
        if count > settings.GPT_MAX_TOKENS:
            raise ValidationError({
                "message": _(
                    f"Enter a valid value that is in the range of {settings.GPT_MAX_TOKENS} tokens"
                ),
                "chunks": "".join(chunks)
                }
            )
