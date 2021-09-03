from rest_framework import serializers

from bothub.common import languages
from bothub.common.models import Repository, QAKnowledgeBase, QAtext


class QAKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAKnowledgeBase
        fields = ["id", "repository", "title", "description"]
        read_only_fields = ["created_at", "last_update"]

    repository = serializers.PrimaryKeyRelatedField(queryset=Repository.objects)
    description = serializers.SerializerMethodField("get_description")

    def get_description(self, obj):
        return obj.get_text_description()


class QAtextSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAtext
        fields = ["id", "text", "language", "knowledge_base"]
        read_only_fields = ["created_at", "last_update"]

    knowledge_base = serializers.PrimaryKeyRelatedField(
        queryset=QAKnowledgeBase.objects
    )
    language = serializers.ChoiceField(languages.LANGUAGE_CHOICES, required=True)
