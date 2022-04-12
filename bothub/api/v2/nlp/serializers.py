from rest_framework import serializers

from django.conf import settings

from bothub.common.models import (
    QAKnowledgeBase,
    QALogs,
    RepositoryNLPLog,
    RepositoryNLPLogIntent,
    RepositoryVersionLanguage,
    RepositoryAuthorization,
)


class NLPSerializer(serializers.Serializer):
    pass


class RepositoryNLPLogIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryNLPLogIntent
        fields = ["intent", "confidence", "is_default"]
        ref_name = None


class RepositoryNLPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryNLPLog
        fields = [
            "id",
            "text",
            "user_agent",
            "repository_version_language",
            "nlp_log",
            "user",
            "log_intent",
            "from_backend",
        ]
        ref_name = None

    log_intent = RepositoryNLPLogIntentSerializer(many=True, required=False)
    repository_version_language = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryVersionLanguage.objects, write_only=True, required=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryAuthorization.objects, write_only=True, required=True
    )

    def create(self, validated_data):
        user = validated_data.get("user").user
        if (
            user.is_organization is False
            and user.user.email in settings.REPOSITORY_BLOCK_USER_LOGS
        ):
            return validated_data  # ToDo: Return a message
        log_intent = validated_data.pop("log_intent")
        validated_data.update({"user": user})

        instance = self.Meta.model(**validated_data)
        instance.save()

        for intent in log_intent:
            RepositoryNLPLogIntent.objects.create(
                intent=intent.get("intent"),
                confidence=intent.get("confidence"),
                is_default=intent.get("is_default"),
                repository_nlp_log=instance,
            )

        return instance


class RepositoryQANLPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QALogs
        fields = [
            "id",
            "answer",
            "confidence",
            "question",
            "user_agent",
            "nlp_log",
            "user",
            "knowledge_base",
            "language",
            "from_backend",
        ]
        ref_name = None

    knowledge_base = serializers.PrimaryKeyRelatedField(
        queryset=QAKnowledgeBase.objects, write_only=True, required=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryAuthorization.objects, write_only=True, required=True
    )

    def create(self, validated_data):
        validated_data.update({"user": validated_data.get("user").user})

        instance = self.Meta.model(**validated_data)
        instance.save()

        return instance
