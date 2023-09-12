# Generated by Django 3.2.20 on 2023-08-30 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0119_repository_count_repository_train'),
        ('project', '0002_projectintelligence'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(blank=True, null=True, verbose_name='UUID')),
                ('name', models.CharField(max_length=255)),
                ('setup', models.JSONField(default=dict)),
            ],
        ),
        migrations.RemoveField(
            model_name='projectintelligence',
            name='repositories',
        ),
        migrations.AddField(
            model_name='projectintelligence',
            name='repository',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_intelligences', to='common.repository'),
        ),
        migrations.AddField(
            model_name='project',
            name='template_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='template_type', to='project.templatetype'),
        ),
    ]