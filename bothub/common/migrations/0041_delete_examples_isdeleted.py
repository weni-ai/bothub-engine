from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def delete_examples_already_deleted(apps, schema_editor):  # pragma: no cover
    RepositoryExample = apps.get_model("common", "RepositoryExample")
    RepositoryEvaluate = apps.get_model("common", "RepositoryEvaluate")
    RepositoryExample.objects.filter(deleted_in__isnull=False).delete()
    RepositoryEvaluate.objects.filter(deleted_in__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [("common", "0040_initial")]

    operations = [migrations.RunPython(delete_examples_already_deleted, noop)]
