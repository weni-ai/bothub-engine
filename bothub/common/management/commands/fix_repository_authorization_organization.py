from django.conf import settings
from django.core.management.base import BaseCommand

from bothub.common.models import RepositoryAuthorization, RequestRepositoryAuthorization


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Updating...")
        old_settings = settings.SEND_EMAILS
        settings.SEND_EMAILS = False
        for auth in RepositoryAuthorization.objects.all():
            if auth.user.is_organization:
                RequestRepositoryAuthorization.objects.create(
                    user=auth.user,
                    repository=auth.repository,
                    approved_by=auth.user,
                )
        settings.SEND_EMAILS = old_settings
