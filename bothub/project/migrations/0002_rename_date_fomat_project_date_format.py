# Generated by Django 3.2.15 on 2023-06-17 01:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='date_fomat',
            new_name='date_format',
        ),
    ]
