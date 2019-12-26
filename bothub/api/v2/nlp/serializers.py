from rest_framework import serializers

from bothub.common.models import (
    RepositoryNLPLog,
    RepositoryNLPLogIntent,
    RepositoryVersionLanguage,
    RepositoryNLPLogEntity,
)


class NLPSerializer(serializers.Serializer):
    pass


class RepositoryNLPLogIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryNLPLogIntent
        fields = ["intent", "confidence", "is_default"]
        ref_name = None


class RepositoryNLPLogEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryNLPLogEntity
        fields = ["entity", "value", "confidence"]
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
            "log_entity",
        ]
        ref_name = None

    log_intent = RepositoryNLPLogIntentSerializer(many=True, required=False)
    log_entity = RepositoryNLPLogEntitySerializer(many=True, required=False)
    repository_version_language = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryVersionLanguage.objects, write_only=True, required=True
    )

    def create(self, validated_data):
        log_intent = validated_data.pop("log_intent")
        log_entity = validated_data.pop("log_entity")

        instance = self.Meta.model(**validated_data)
        instance.save()

        for intent in log_intent:
            RepositoryNLPLogIntent.objects.create(
                intent=intent.get("intent"),
                confidence=intent.get("confidence"),
                is_default=intent.get("is_default"),
                repository_nlp_log=instance,
            )

        for entity in log_entity:
            RepositoryNLPLogEntity.objects.create(
                entity=entity.get("entity"),
                value=entity.get("value"),
                confidence=entity.get("confidence"),
                repository_nlp_log=instance,
            )

        return instance
