# Generated by Django 2.2.17 on 2021-03-11 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("common", "0106_auto_20210311_1254")]

    operations = [
        migrations.AlterUniqueTogether(
            name="qacontext", unique_together={("knowledge_base", "language")}
        )
    ]
