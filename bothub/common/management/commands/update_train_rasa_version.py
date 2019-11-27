import datetime

from django.core.management.base import BaseCommand

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Updating...")
        RepositoryUpdate.objects.all().update(updated_rasa=False)
        for repository in Repository.objects.all():
            update = repository.updates.filter(
                by__isnull=False,
                trained_at__isnull=False,
                created_at__gte=datetime.date(2019, 11, 11),
            )
            for u in update:
                u.updated_rasa = True
                u.save(update_fields=["updated_rasa"])
                print("RepositoryUpdate ID {} Updated".format(u.pk))
