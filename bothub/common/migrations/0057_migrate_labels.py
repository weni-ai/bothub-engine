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

    for repository in Repository.objects.all():

        for repository_version in RepositoryVersion.objects.filter(repository=repository):
            old_labels = RepositoryEntityLabel.objects.filter(repository=repository_version.repository)
            for label in old_labels:
                RepositoryEntityGroup.objects.create(
                    repository_version=repository_version,
                    value=label.value
                )

        for entity_version in RepositoryEntity.objects.filter(repository=repository):
            if entity_version.label:
                entity_version.group = RepositoryEntityGroup.objects.filter(pk=entity_version.label.pk).first()

            entity_version.repository_version = RepositoryVersion.objects.get(repository=repository, is_default=True)
            entity_version.save(update_fields=["group", "repository_version"])

            for version in RepositoryVersion.objects.filter(repository=repository, is_default=False):
                if entity_version.label:
                    RepositoryEntity.objects.create(
                        repository=entity_version.repository,
                        value=entity_version.value,
                        group=RepositoryEntityGroup.objects.filter(repository_version=version, value=entity_version.label.value).first(),
                        repository_version=version
                    )
                else:
                    RepositoryEntity.objects.create(
                        repository=entity_version.repository,
                        value=entity_version.value,
                        repository_version=version
                    )

        for example_entity in RepositoryExampleEntity.objects.all():
            print(example_entity.repository_example.repository_version_language.repository_version)




class Migration(migrations.Migration):

    dependencies = [("common", "0056_auto_20200520_1220")]

    operations = [migrations.RunPython(migrate, noop)]
