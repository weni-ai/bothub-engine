# Generated by Django 2.1.11 on 2019-10-11 20:21

import django.utils.timezone
from django.db import migrations, models
from django.conf import settings
from bothub.utils import send_bot_data_file_aws
from bothub.common.models import RepositoryUpdate


def update_repository(apps, schema_editor):
    if settings.AWS_SEND:
        for update in RepositoryUpdate.objects.all().exclude(bot_data__exact=""):
            repository_update = RepositoryUpdate.objects.get(pk=update.pk)
            bot_data = send_bot_data_file_aws(update.pk, update.bot_data)
            repository_update.bot_data = bot_data
            repository_update.save(update_fields=["bot_data"])
            print("Updating bot_data repository_update {}".format(str(update.pk)))


class Migration(migrations.Migration):

    dependencies = [("common", "0032_repository_total_updates")]

    operations = [
        migrations.RemoveField(model_name="repositoryvote", name="vote"),
        migrations.AddField(
            model_name="repository",
            name="nlp_server",
            field=models.URLField(blank=True, null=True, verbose_name="Base URL NLP"),
        ),
        migrations.AddField(
            model_name="repositoryvote",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.RunPython(update_repository),
        migrations.AlterField(
            model_name="repositoryupdate",
            name="bot_data",
            field=models.TextField(blank=True, verbose_name="bot data"),
        ),
    ]
