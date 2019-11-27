from django.core.management.base import BaseCommand

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Updating...")
        RepositoryUpdate.objects.all().update(publish=False)
        for repository in Repository.objects.all():
            for lang in repository.available_languages:
                update = repository.updates.filter(
                    language=lang, by__isnull=False, trained_at__isnull=False
                ).first()
                if update is not None:
                    update.define_publish()
                    print("RepositoryUpdate ID {} Updated".format(update.pk))
