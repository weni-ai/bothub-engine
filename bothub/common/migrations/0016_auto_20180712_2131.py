# Generated by Django 2.0.6 on 2018-07-12 21:31

import bothub.common.languages
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("common", "0015_auto_20180712_2130")]

    operations = [
        migrations.AlterField(
            model_name="repositoryupdate",
            name="language",
            field=models.CharField(
                max_length=5,
                validators=[bothub.common.languages.validate_language],
                verbose_name="language",
            ),
        )
    ]
