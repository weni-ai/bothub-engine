from django.db import transaction
from django.conf import settings
from bothub.common.tasks import handle_save
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor


class CelerySignalProcessor(RealTimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        model = instance._meta.concrete_model

        if settings.USE_ELASTICSEARCH and (
            model in registry._models or model in registry._related_models
        ):
            transaction.on_commit(
                lambda: handle_save.apply_async(
                    args=[instance.pk, app_label, model_name],
                    queue=settings.ELASTICSEARCH_CUSTOM_QUEUE,
                )
            )

    def handle_pre_delete(self, sender, instance, **kwargs):
        """
        Logs deletions are now handled in delete_nlp_logs task
        """
        pass

    def handle_delete(self, sender, instance, **kwargs):
        """
        Logs deletions are now handled in delete_nlp_logs task
        """
        pass
