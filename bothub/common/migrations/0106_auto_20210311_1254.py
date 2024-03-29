# Generated by Django 2.2.17 on 2021-03-11 12:54

import bothub.common.languages
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("common", "0105_auto_20210309_1945")]

    operations = [
        migrations.RemoveField(model_name="qaknowledgebase", name="language"),
        migrations.RemoveField(model_name="qaknowledgebase", name="text"),
        migrations.CreateModel(
            name="QAContext",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="QA context text",
                        max_length=25000,
                        verbose_name="text",
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        help_text="Knowledge Base language",
                        max_length=5,
                        validators=[bothub.common.languages.validate_language],
                        verbose_name="language",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "last_update",
                    models.DateTimeField(auto_now=True, verbose_name="last update"),
                ),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contexts",
                        to="common.QAKnowledgeBase",
                    ),
                ),
            ],
        ),
    ]
