# Generated by Django 2.1.5 on 2019-08-14 19:45

from django.db import migrations, models

from bothub.common.models import RepositoryUpdate
from bothub.common.models import Repository


def updateRepository(apps, schema_editor):
    for update in RepositoryUpdate.objects.all().filter(trained_at__isnull=False):
        repository = Repository.objects.get(uuid=update.repository.uuid)
        repository.total_updates += 1
        repository.save()


class Migration(migrations.Migration):

    dependencies = [("common", "0031_auto_20190502_1732")]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="total_updates",
            field=models.IntegerField(default=0, verbose_name="total updates"),
        ),
        migrations.RunPython(updateRepository),
    ]