import threading
from django.core.management.base import BaseCommand

from bothub.common.models import RepositoryVersion


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        repository_version_language = RepositoryVersion.objects.all()

        for version in repository_version_language:
            user_authorization = version.repository.get_user_authorization(user=version.repository.owner)

            t = threading.Thread(
                target=version.repository.request_nlp_train,
                args=(
                    user_authorization,
                    {"repository_version": version.pk}
                )
             )
            t.start()
