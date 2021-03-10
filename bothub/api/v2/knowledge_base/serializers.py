from rest_framework import serializers

from bothub.common import languages
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import Repository, QAKnowledgeBase


class QAKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAKnowledgeBase
        fields = ["repository", "title", "text", "language"]
        read_only_fields = ["id", "created_at", "last_update"]

    repository = serializers.PrimaryKeyRelatedField(queryset=Repository.objects)
    language = serializers.ChoiceField(languages.LANGUAGE_CHOICES, required=True)


class QASerializer(serializers.Serializer):
    context = serializers.CharField(max_length=25000)
    question = serializers.CharField(max_length=500)
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
