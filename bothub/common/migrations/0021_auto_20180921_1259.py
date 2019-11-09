# Generated by Django 2.0.6 on 2018-09-21 12:59

import django.core.validators
from django.db import migrations, models
import re


def populate_empty_intent(apps, *args):
    RepositoryExample = apps.get_model("common", "RepositoryExample")
    RepositoryExample.objects.filter(intent="").update(intent="no_intent")


class Migration(migrations.Migration):

    dependencies = [("common", "0020_auto_20180813_1320")]

    operations = [
        migrations.AlterField(
            model_name="repositoryexample",
            name="intent",
            field=models.CharField(
                default="no_intent",
                help_text="Example intent reference",
                max_length=64,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-z0-9_]+\\Z"),
                        "Enter a valid value consisting of lowercase letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="intent",
            ),
        ),
        migrations.RunPython(populate_empty_intent),
    ]
