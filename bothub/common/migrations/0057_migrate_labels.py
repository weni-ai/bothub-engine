from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    RepositoryVersion = apps.get_model("common", "RepositoryVersion")
    RepositoryEntityLabel = apps.get_model("common", "RepositoryEntityLabel")
    RepositoryEntityGroup = apps.get_model("common", "RepositoryEntityGroup")

    for repository_version in RepositoryVersion.objects.all():
        print(repository_version.repository)
        old_labels = RepositoryEntityLabel.objects.filter(repository=repository_version.repository)
        print(old_labels)
        for label in old_labels:
            print(label.value)


class Migration(migrations.Migration):

    dependencies = [("common", "0056_auto_20200520_1220")]

    operations = [migrations.RunPython(migrate, noop)]
