from django.core.management.base import BaseCommand
from django.utils import timezone

from bothub.common.models import RepositoryVersionLanguage


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        RepositoryVersionLanguage.objects.all().update(last_update=timezone.now())
        print('END')
