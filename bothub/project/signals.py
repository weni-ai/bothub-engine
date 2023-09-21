from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from bothub.project.models import ProjectIntelligence
from bothub.event_driven.publisher.rabbitmq_publisher import RabbitMQPublisher

@receiver(post_save, sender=ProjectIntelligence)
def integrate_ai(sender, instance, created, **kwargs):

    if created:
        rabbitmq_publisher = RabbitMQPublisher()
        body = {
            "uuid": str(instance.uuid),
            "access_token": str(instance.access_token),
            "name": instance.name,
            "repository": str(instance.repository.uuid),
            "project_uuid": str(instance.project.uuid),
            "user_email": instance.integrated_by.email,
        }
        rabbitmq_publisher.send_message(body=body, exchange="intelligences.topic", routing_key="")
