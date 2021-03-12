from rest_framework import serializers

from bothub.common import languages
from bothub.common.models import Repository, QAKnowledgeBase, QAContext


class QAKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAKnowledgeBase
        fields = ["id", "repository", "title"]
        read_only_fields = ["created_at", "last_update"]

    repository = serializers.PrimaryKeyRelatedField(queryset=Repository.objects)


class QAContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAContext
        fields = ["id", "text", "language", "knowledge_base"]
        read_only_fields = ["created_at", "last_update"]

    knowledge_base = serializers.PrimaryKeyRelatedField(
        queryset=QAKnowledgeBase.objects
    )
    language = serializers.ChoiceField(languages.LANGUAGE_CHOICES, required=True)
