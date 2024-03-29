# Generated by Django 3.2.15 on 2023-03-31 01:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0115_auto_20220923_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZeroShotOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_uuid', models.UUIDField(default=uuid.UUID('b71948e5-abd5-47b3-8aff-4bfcc1ad4bca'))),
                ('key', models.TextField(help_text='option key')),
            ],
        ),
        migrations.AlterField(
            model_name='repository',
            name='repository_type',
            field=models.CharField(choices=[('classifier', 'Classifier'), ('content', 'Content'), ('zeroshot', 'Zero shot')], default='classifier', max_length=10, verbose_name='repository type'),
        ),
        migrations.CreateModel(
            name='ZeroShotOptionsText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='text make reference to a option')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.zeroshotoptions')),
            ],
        ),
        migrations.CreateModel(
            name='RepositoryZeroShot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Text to analyze')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('zeroshot_log', models.TextField(blank=True, help_text='NLP Log')),
                ('ended_at', models.DateTimeField(blank=True, verbose_name='ended at')),
                ('options', models.ManyToManyField(blank=True, related_name='repository_options', to='common.ZeroShotOptionsText')),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.repository')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
