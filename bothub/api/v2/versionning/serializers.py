from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from bothub.api.v2.repository.validators import CanContributeInRepositoryValidator
from bothub.api.v2.versionning.validators import (
    CanUseNameVersionValidator,
    VersionNameNotExistValidator,
)
from bothub.common.models import (
    RepositoryVersion,
    RepositoryExample,
    RepositoryTranslatedExample,
    RepositoryTranslatedExampleEntity,
    RepositoryExampleEntity,
    RepositoryEvaluate,
    RepositoryEvaluateEntity,
    RepositoryVersionLanguage,
    Repository,
)


class RepositoryVersionSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVersion
        fields = [
            "id",
            "repository",
            "name",
            "is_default",
            "created_at",
            "created_by",
            "last_update",
        ]
        ref_name = None

        read_only = ["is_default", "created_by", "last_update"]

    is_default = serializers.BooleanField(default=False, required=False)
    id = serializers.IntegerField()
    name = serializers.CharField(
        max_length=40, required=True, validators=[CanUseNameVersionValidator()]
    )
    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        validators=[CanContributeInRepositoryValidator()],
        write_only=True,
        style={"show": False},
    )
    created_by = serializers.CharField(source="created_by.name", read_only=True)
    last_update = serializers.DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(VersionNameNotExistValidator())

    def update(self, instance, validated_data):
        validated_data.pop("repository")
        if validated_data.get("is_default"):
            validated_data["is_default"] = True
            RepositoryVersion.objects.filter(repository=instance.repository).update(
                is_default=False
            )
        return super().update(instance, validated_data)

    def create(self, validated_data):  # pragma: no cover
        if True:
            return {}
        id_clone = validated_data.pop("id")
        repository = validated_data.get("repository")
        name = validated_data.get("name")
        clone = get_object_or_404(RepositoryVersion, pk=id_clone, repository=repository)

        instance = self.Meta.model(
            name=name,
            last_update=clone.last_update,
            is_default=False,
            repository=clone.repository,
            created_by=self.context["request"].user,
        )
        instance.save()

        for version in clone.version_languages:

            version_language = RepositoryVersionLanguage.objects.create(
                language=version.language,
                bot_data=version.bot_data,
                training_started_at=version.training_started_at,
                training_end_at=version.training_end_at,
                failed_at=version.failed_at,
                use_analyze_char=version.use_analyze_char,
                use_name_entities=version.use_name_entities,
                use_competing_intents=version.use_competing_intents,
                algorithm=version.algorithm,
                repository_version=instance,
                training_log=version.training_log,
                last_update=version.last_update,
                total_training_end=version.total_training_end,
            )

            examples = RepositoryExample.objects.filter(
                repository_version_language=version
            )

            for example in examples:
                example_id = RepositoryExample.objects.create(
                    repository_version_language=version_language,
                    text=example.text,
                    intent=example.intent,
                    created_at=example.created_at,
                    last_update=example.last_update,
                )

                example_entites = RepositoryExampleEntity.objects.filter(
                    repository_example=example
                )

                for example_entity in example_entites:
                    RepositoryExampleEntity.objects.create(
                        repository_example=example_id,
                        start=example_entity.start,
                        end=example_entity.end,
                        entity=example_entity.entity,
                        created_at=example_entity.created_at,
                    )

                translated_examples = RepositoryTranslatedExample.objects.filter(
                    original_example=example
                )

                for translated_example in translated_examples:
                    translated = RepositoryTranslatedExample.objects.create(
                        repository_version_language=version_language,
                        original_example=example_id,
                        language=translated_example.language,
                        text=translated_example.text,
                        created_at=translated_example.created_at,
                        clone_repository=True,
                    )

                    translated_entity_examples = RepositoryTranslatedExampleEntity.objects.filter(
                        repository_translated_example=translated
                    )

                    for translated_entity in translated_entity_examples:
                        RepositoryTranslatedExampleEntity.objects.create(
                            repository_translated_example=translated,
                            start=translated_entity.start,
                            end=translated_entity.end,
                            entity=translated_entity.entity,
                            created_at=translated_entity.created_at,
                        )

            evaluates = RepositoryEvaluate.objects.filter(
                repository_version_language=version
            )

            for evaluate in evaluates:
                evaluate_id = RepositoryEvaluate.objects.create(
                    repository_version_language=version_language,
                    text=evaluate.text,
                    intent=evaluate.intent,
                    created_at=evaluate.created_at,
                )

                evaluate_entities = RepositoryEvaluateEntity.objects.filter(
                    repository_evaluate=evaluate_id
                )

                for evaluate_entity in evaluate_entities:
                    RepositoryEvaluateEntity.objects.create(
                        repository_evaluate=evaluate_id,
                        start=evaluate_entity.start,
                        end=evaluate_entity.end,
                        entity=evaluate_entity.entity,
                        created_at=evaluate_entity.created_at,
                    )

        return instance
