from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    RepositoryVersion = apps.get_model("common", "RepositoryVersion")
    RepositoryEntity = apps.get_model("common", "RepositoryEntity")
    RepositoryExampleEntity = apps.get_model("common", "RepositoryExampleEntity")

    for repository_version in RepositoryVersion.objects.all():
        RepositoryEntity.objects.exclude(
            pk__in=RepositoryExampleEntity.objects.filter(
                repository_example__repository_version_language__repository_version=repository_version
            ).values("entity")
        ).filter(repository_version=repository_version).delete()


class Migration(migrations.Migration):

    dependencies = [("common", "0061_labels")]

    operations = [migrations.RunPython(migrate, noop)]
