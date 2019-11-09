from django.core.management.base import BaseCommand

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Updating...")
        Repository.objects.all().update(total_updates=0)
        for update in RepositoryUpdate.objects.all().filter(trained_at__isnull=False):
            repository = Repository.objects.get(uuid=update.repository.uuid)
            repository.total_updates += 1
            repository.save()
            print("Repository UUID {} Updated".format(repository.pk))
