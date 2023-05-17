# Generated by Django 3.2.15 on 2023-05-17 17:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0117_alter_zeroshotoptions_option_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='repositoryevaluateresult',
            name='evaluate_type',
            field=models.PositiveIntegerField(blank=True, choices=[(0, 'manual'), (1, 'automatic')], default=0, null=True, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='zeroshotoptions',
            name='option_uuid',
            field=models.UUIDField(default=uuid.UUID('4e0cf37b-a6b2-40fd-a3cb-cce5bda8e14e')),
        ),
    ]
