from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    Repository = apps.get_model("common", "Repository")
    RepositoryVersion = apps.get_model("common", "RepositoryVersion")
    RepositoryEntityLabel = apps.get_model("common", "RepositoryEntityLabel")
    RepositoryEntityGroup = apps.get_model("common", "RepositoryEntityGroup")
    RepositoryEntity = apps.get_model("common", "RepositoryEntity")
    RepositoryExampleEntity = apps.get_model("common", "RepositoryExampleEntity")
    RepositoryTranslatedExampleEntity = apps.get_model(
        "common", "RepositoryTranslatedExampleEntity"
    )

    for repository in Repository.objects.all():
        for repository_version in RepositoryVersion.objects.filter(
            repository=repository
        ):
            old_labels = RepositoryEntityLabel.objects.filter(
                repository=repository_version.repository
            )
            for label in old_labels:
                RepositoryEntityGroup.objects.create(
                    repository_version=repository_version, value=label.value
                )

        for entity_version in RepositoryEntity.objects.filter(repository=repository):
            entity_version.repository_version = RepositoryVersion.objects.get(
                repository=repository, is_default=True
            )
            entity_version.save(update_fields=["repository_version"])

            for version in RepositoryVersion.objects.filter(
                repository=repository, is_default=False
            ):
                RepositoryEntity.objects.create(
                    repository=entity_version.repository,
                    value=entity_version.value,
                    repository_version=version,
                )

    for example_entity in RepositoryExampleEntity.objects.all():
        if (
            not example_entity.repository_example.repository_version_language.repository_version.is_default
        ):
            example_entity.entity = RepositoryEntity.objects.filter(
                repository_version=example_entity.repository_example.repository_version_language.repository_version,
                value=example_entity.entity.value,
            ).first()
            example_entity.save(update_fields=["entity"])

    for example_translated_entity in RepositoryTranslatedExampleEntity.objects.all():
        if (
            not example_translated_entity.repository_translated_example.repository_version_language.repository_version.is_default
        ):
            example_translated_entity.entity = RepositoryEntity.objects.filter(
                repository_version=example_translated_entity.repository_translated_example.repository_version_language.repository_version,
                value=example_translated_entity.entity.value,
            ).first()
            example_translated_entity.save(update_fields=["entity"])


class Migration(migrations.Migration):

    dependencies = [("common", "0056_auto_20200520_1220")]

    operations = [migrations.RunPython(migrate, noop)]
