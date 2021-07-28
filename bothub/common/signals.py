from django.db import transaction
from bothub.common.tasks import handle_save, handle_pre_delete, handle_delete
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor


class CelerySignalProcessor(RealTimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        model = instance._meta.concrete_model
        if model in registry._models or model in registry._related_models:
            transaction.on_commit(
                lambda: handle_save.delay(instance.pk, app_label, model_name)
            )

    def handle_pre_delete(self, sender, instance, **kwargs):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        model = instance._meta.concrete_model
        if model in registry._models or model in registry._related_models:
            handle_pre_delete.delay(instance.pk, app_label, model_name)

    def handle_delete(self, sender, instance, **kwargs):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        model = instance._meta.concrete_model
        if model in registry._models or model in registry._related_models:
            handle_delete.delay(instance.pk, app_label, model_name)
