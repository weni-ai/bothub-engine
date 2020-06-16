from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def delete_evaluates_already_deleted(apps, schema_editor):  # pragma: no cover
    RepositoryEvaluate = apps.get_model("common", "RepositoryEvaluate")
    RepositoryEvaluate.objects.filter(deleted_in__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [("common", "0051_auto_20200403_1919")]

    operations = [migrations.RunPython(delete_evaluates_already_deleted, noop)]
