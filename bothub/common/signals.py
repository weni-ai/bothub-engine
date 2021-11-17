from django.db import transaction
from bothub.celery import app as celery_app
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor


class CelerySignalProcessor(RealTimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        model = instance._meta.concrete_model
        if model in registry._models or model in registry._related_models:
            transaction.on_commit(
                lambda: celery_app.send_task(
                    "es_handle_save", args=[instance.pk, app_label, model_name]
                )
            )

    def handle_pre_delete(self, sender, instance, **kwargs):
        pass

    def handle_delete(self, sender, instance, **kwargs):
        pass
