from django.db import migrations


def noop(apps, schema_editor):  # pragma: no cover
    pass


def migrate(apps, schema_editor):  # pragma: no cover
    RepositoryTranslatedExample = apps.get_model(
        "common", "RepositoryTranslatedExample"
    )
    RepositoryVersionLanguage = apps.get_model("common", "RepositoryVersionLanguage")

    for translated in list(RepositoryTranslatedExample.objects.all().iterator()):
        if translated.repository_version_language is None:
            (
                repository_version_language,
                created,
            ) = RepositoryVersionLanguage.objects.get_or_create(
                repository_version=translated.original_example.repository_version_language.repository_version,
                language=translated.language,
            )
            translated.repository_version_language = repository_version_language
            translated.save(update_fields=["repository_version_language"])
            continue
        if translated.repository_version_language.language != translated.language:
            (
                repository_version_language,
                created,
            ) = RepositoryVersionLanguage.objects.get_or_create(
                repository_version=translated.repository_version_language.repository_version,
                language=translated.language,
            )
            translated.repository_version_language = repository_version_language
            translated.save(update_fields=["repository_version_language"])


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0067_repositoryversionlanguage_use_transformer_entities")
    ]

    operations = [migrations.RunPython(migrate, noop)]
