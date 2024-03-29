# Generated by Django 3.2.21 on 2023-10-16 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0119_repository_count_repository_train'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZeroshotLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Text to analyze')),
                ('classification', models.TextField()),
                ('other', models.BooleanField()),
                ('categories', models.JSONField()),
                ('nlp_log', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'zeroshot nlp logs',
            },
        ),
        migrations.AddIndex(
            model_name='zeroshotlogs',
            index=models.Index(fields=['nlp_log'], name='common_zeroshot_log_idx'),
        ),
    ]
