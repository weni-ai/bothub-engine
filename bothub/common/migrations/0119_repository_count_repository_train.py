# Generated by Django 3.2.20 on 2023-07-13 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0118_alter_zeroshotoptions_option_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='count_repository_train',
            field=models.IntegerField(default=0, verbose_name='Train count'),
        ),
    ]
