from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F, Q

from bothub.common.models import RepositoryTranslatedExample

BATCH_SIZE = 5000


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        translations = RepositoryTranslatedExample.objects.exclude(
            Q(repository_version_language__language=F("language"))
        )

        num_updated = 0
        max_id = -1
        while True:
            batch = list(translations.filter(id__gt=max_id).order_by("id")[:BATCH_SIZE])
            if not batch:
                break

            with transaction.atomic():
                for translation in batch:
                    repository_version_language = translation.original_example.repository_version_language.repository_version.get_version_language(
                        translation.language
                    )
                    translation.repository_version_language = (
                        repository_version_language
                    )
                    translation.save(update_fields=["repository_version_language"])

            num_updated += len(batch)
            print(f" > Updated {num_updated} translations")

            max_id = batch[-1].id
