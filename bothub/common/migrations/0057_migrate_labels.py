from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    Repository = apps.get_model("common", "Repository")
    RepositoryEntityLabel = apps.get_model("common", "RepositoryEntityLabel")

    for repo in Repository.objects.all():
        print(repo)


class Migration(migrations.Migration):

    dependencies = [("common", "0056_auto_20200520_1220")]

    operations = [migrations.RunPython(migrate, noop)]
