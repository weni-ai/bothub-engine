from celery import shared_task
from django.apps import apps
from django.db import transaction
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor


@shared_task
def handle_save(pk, app_label, model_name):
    sender = apps.get_model(app_label, model_name)
    instance = sender.objects.get(pk=pk)
    registry.update(instance)
    registry.update_related(instance)


@shared_task
def handle_pre_delete(pk, app_label, model_name):
    sender = apps.get_model(app_label, model_name)
    instance = sender.objects.get(pk=pk)
    registry.delete_related(instance)


@shared_task
def handle_delete(pk, app_label, model_name):
    sender = apps.get_model(app_label, model_name)
    instance = sender.objects.get(pk=pk)
    registry.delete(instance, raise_on_error=False)


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
