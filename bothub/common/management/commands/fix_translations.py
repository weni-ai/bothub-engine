from django.core.management.base import BaseCommand

from bothub.common.models import RepositoryTranslatedExample


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for translated in RepositoryTranslatedExample.objects.all():
            if translated.language != translated.repository_version_language.language:
                language_version = translated.repository_version_language.repository_version.get_version_language(
                    language=translated.language
                )
                translated.repository_version_language = language_version
                translated.save(update_fields=['repository_version_language'])
