# Generated by Django 2.1.5 on 2019-05-02 17:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [("common", "0030_auto_20190327_2003")]

    operations = [
        migrations.CreateModel(
            name="RepositoryEvaluate",
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
                        help_text="Evaluate test text", verbose_name="text"
                    ),
                ),
                (
                    "intent",
                    models.CharField(
                        default="no_intent",
                        help_text="Evaluate intent reference",
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-z0-9_]+\\Z"),
                                "Enter a valid value consisting of lowercase letters, numbers, underscores or hyphens.",
                                "invalid",
                            )
                        ],
                        verbose_name="intent",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "deleted_in",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deleted_evaluate",
                        to="common.RepositoryUpdate",
                    ),
                ),
                (
                    "repository_update",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="added_evaluate",
                        to="common.RepositoryUpdate",
                    ),
                ),
            ],
            options={
                "verbose_name": "repository evaluate test",
                "verbose_name_plural": "repository evaluate tests",
                "db_table": "common_repository_evaluate",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="RepositoryEvaluateEntity",
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
                    "start",
                    models.PositiveIntegerField(
                        help_text="Start index of entity value in example text",
                        verbose_name="start",
                    ),
                ),
                (
                    "end",
                    models.PositiveIntegerField(
                        help_text="End index of entity value in example text",
                        verbose_name="end",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="common.RepositoryEntity",
                    ),
                ),
                (
                    "repository_evaluate",
                    models.ForeignKey(
                        editable=False,
                        help_text="evaluate object",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entities",
                        to="common.RepositoryEvaluate",
                    ),
                ),
            ],
            options={"db_table": "common_repository_evaluate_entity"},
        ),
        migrations.CreateModel(
            name="RepositoryEvaluateResult",
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
                    "matrix_chart",
                    models.URLField(
                        editable=False, verbose_name="Intent Confusion Matrix Chart"
                    ),
                ),
                (
                    "confidence_chart",
                    models.URLField(
                        editable=False,
                        verbose_name="Intent Prediction Confidence Distribution",
                    ),
                ),
                (
                    "log",
                    models.TextField(
                        blank=True, editable=False, verbose_name="Evaluate Log"
                    ),
                ),
                (
                    "version",
                    models.IntegerField(
                        default=0, editable=False, verbose_name="Version"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
            ],
            options={
                "verbose_name": "evaluate results",
                "verbose_name_plural": "evaluate results",
                "db_table": "common_repository_evaluate_result",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="RepositoryEvaluateResultEntity",
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
                    "entity",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entity",
                        to="common.RepositoryEntity",
                    ),
                ),
                (
                    "evaluate_result",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluate_result_entity",
                        to="common.RepositoryEvaluateResult",
                    ),
                ),
            ],
            options={"db_table": "common_repository_evaluate_result_entity"},
        ),
        migrations.CreateModel(
            name="RepositoryEvaluateResultIntent",
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
                    "intent",
                    models.CharField(
                        help_text="Evaluate intent reference",
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-z0-9_]+\\Z"),
                                "Enter a valid value consisting of lowercase letters, numbers, underscores or hyphens.",
                                "invalid",
                            )
                        ],
                        verbose_name="intent",
                    ),
                ),
                (
                    "evaluate_result",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluate_result_intent",
                        to="common.RepositoryEvaluateResult",
                    ),
                ),
            ],
            options={"db_table": "common_repository_evaluate_result_intent"},
        ),
        migrations.CreateModel(
            name="RepositoryEvaluateResultScore",
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
                    "precision",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                (
                    "f1_score",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                (
                    "accuracy",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                (
                    "recall",
                    models.DecimalField(decimal_places=2, max_digits=3, null=True),
                ),
                ("support", models.IntegerField(null=True)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
            ],
            options={
                "db_table": "common_repository_evaluate_result_score",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="repositoryevaluateresultintent",
            name="score",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="evaluation_intenties_score",
                to="common.RepositoryEvaluateResultScore",
            ),
        ),
        migrations.AddField(
            model_name="repositoryevaluateresultentity",
            name="score",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="evaluation_entities_score",
                to="common.RepositoryEvaluateResultScore",
            ),
        ),
        migrations.AddField(
            model_name="repositoryevaluateresult",
            name="entity_results",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="entity_results",
                to="common.RepositoryEvaluateResultScore",
            ),
        ),
        migrations.AddField(
            model_name="repositoryevaluateresult",
            name="intent_results",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="intent_results",
                to="common.RepositoryEvaluateResultScore",
            ),
        ),
        migrations.AddField(
            model_name="repositoryevaluateresult",
            name="repository_update",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="results",
                to="common.RepositoryUpdate",
            ),
        ),
    ]
