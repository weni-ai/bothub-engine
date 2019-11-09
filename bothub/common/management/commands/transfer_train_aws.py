from django.conf import settings
from django.core.management.base import BaseCommand

from bothub.common.models import RepositoryUpdate
from bothub.utils import send_bot_data_file_aws


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if settings.AWS_SEND:
            for update in RepositoryUpdate.objects.all().exclude(bot_data__exact=""):
                repository_update = RepositoryUpdate.objects.get(pk=update.pk)
                bot_data = send_bot_data_file_aws(update.pk, update.bot_data)
                repository_update.bot_data = bot_data
                repository_update.save(update_fields=["bot_data"])
                print("Updating bot_data repository_update {}".format(str(update.pk)))
        else:
            print("You need to configure the environment variables for AWS.")
