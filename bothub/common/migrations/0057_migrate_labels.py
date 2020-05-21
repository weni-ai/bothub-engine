from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    Repository = apps.get_model("common", "Repository")
    RepositoryVersion = apps.get_model("common", "RepositoryVersion")
    RepositoryEntityGroup = apps.get_model("common", "RepositoryEntityGroup")
    RepositoryEntity = apps.get_model("common", "RepositoryEntity")
    RepositoryExampleEntity = apps.get_model("common", "RepositoryExampleEntity")
    RepositoryTranslatedExampleEntity = apps.get_model(
        "common", "RepositoryTranslatedExampleEntity"
    )

    for repository in Repository.objects.all():
        for entity_version in RepositoryEntity.objects.filter(repository=repository):
            repository_version = RepositoryVersion.objects.get(
                repository=repository, is_default=True
            )
            entity_version.repository_version = repository_version
            if entity_version.label:
                group, created = RepositoryEntityGroup.objects.get_or_create(
                    repository_version=repository_version,
                    value=entity_version.label.value,
                )
                entity_version.group = group
            entity_version.save(update_fields=["group", "repository_version"])

            for version in RepositoryVersion.objects.filter(
                repository=repository, is_default=False
            ):
                if entity_version.group:
                    group_version, created = RepositoryEntityGroup.objects.get_or_create(
                        repository_version=version, value=entity_version.group.value
                    )
                    RepositoryEntity.objects.create(
                        repository=entity_version.repository,
                        value=entity_version.value,
                        repository_version=version,
                        group=group_version,
                    )
                else:
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
