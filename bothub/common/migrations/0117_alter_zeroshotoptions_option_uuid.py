# Generated by Django 3.2.15 on 2023-03-31 03:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0116_auto_20230331_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zeroshotoptions',
            name='option_uuid',
            field=models.UUIDField(default=uuid.UUID('e740f18a-14bd-42e4-b744-cfa75e867188')),
        ),
    ]