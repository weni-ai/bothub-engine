from rest_framework import serializers

from bothub.common.models import (
    RepositoryUpdate,
    RepositoryExample,
    RepositoryTranslatedExample,
    RepositoryTranslatedExampleEntity,
    RepositoryExampleEntity,
    RepositoryEvaluate,
    RepositoryEvaluateEntity,
)


class RepositoryVersionSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = ["id", "repository", "language", "selected", "created_at"]
        ref_name = None

        read_only = ["language", "selected"]

    selected = serializers.BooleanField(default=True, read_only=True, required=False)
    language = serializers.CharField(required=False)
    id = serializers.IntegerField()

    def update(self, instance, validated_data):
        validated_data.pop("repository")
        validated_data["selected"] = True
        RepositoryUpdate.objects.filter(
            repository=instance.repository, language=instance.language
        ).update(selected=False)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        id_clone = validated_data.pop("id")
        clone = RepositoryUpdate.objects.get(pk=id_clone)

        instance = self.Meta.model(
            repository=clone.repository,
            language=clone.language,
            algorithm=clone.algorithm,
            use_competing_intents=clone.use_competing_intents,
            use_name_entities=clone.use_name_entities,
            bot_data=clone.bot_data,
            by=clone.by,
            training_started_at=clone.training_started_at,
            trained_at=clone.trained_at,
            failed_at=clone.failed_at,
            training_log=clone.training_log,
            use_analyze_char=clone.use_analyze_char,
            last_update=clone.last_update,
            selected=False,
        )
        instance.save()

        examples = RepositoryExample.objects.filter(repository_update=id_clone)

        for example in examples:
            if example.deleted_in:
                example_id = RepositoryExample.objects.create(
                    repository_update=instance,
                    deleted_in=instance,
                    text=example.text,
                    intent=example.intent,
                    created_at=example.created_at,
                    last_update=example.last_update,
                )
            else:
                example_id = RepositoryExample.objects.create(
                    repository_update=instance,
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
                    repository_update=instance,
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

        evaluates = RepositoryEvaluate.objects.filter(repository_update=id_clone)

        for evaluate in evaluates:
            if evaluate.deleted_in:
                evaluate_id = RepositoryEvaluate.objects.create(
                    repository_update=instance,
                    deleted_in=instance,
                    text=evaluate.text,
                    intent=evaluate.intent,
                    created_at=evaluate.created_at,
                )
            else:
                evaluate_id = RepositoryEvaluate.objects.create(
                    repository_update=instance,
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
