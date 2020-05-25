from django.db import migrations
from django.conf import settings


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    RepositoryVersionLanguage = apps.get_model("common", "RepositoryVersionLanguage")
    RepositoryNLPTrain = apps.get_model("common", "RepositoryNLPTrain")

    for version in RepositoryVersionLanguage.objects.all():
        if version.bot_data:
            RepositoryNLPTrain.objects.create(
                bot_data=version.bot_data,
                repositoryversionlanguage=version,
                rasa_version=settings.BOTHUB_NLP_RASA_VERSION,
            )


class Migration(migrations.Migration):

    dependencies = [("common", "0056_auto_20200522_1120")]

    operations = [
        migrations.RunPython(migrate, noop),
        migrations.RemoveField(model_name="repositoryversionlanguage", name="bot_data"),
    ]
