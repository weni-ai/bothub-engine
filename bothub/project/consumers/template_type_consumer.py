import amqp

from bothub.event_driven.parsers import JSONParser
from bothub.event_driven.consumers import EDAConsumer
from ..usecases.template_type_creation import create_template_type


class TemplateTypeConsumer(EDAConsumer):  # pragma: no cover
    def consume(self, message: amqp.Message):
        body = JSONParser.parse(message.body)

        print(f"[TemplateTypeConsumer] - Consuming a message. Body: {body}")

        create_template_type(uuid=body.get("uuid"), project_uuid=body.get("project_uuid"), name=body.get("name"))

        message.channel.basic_ack(message.delivery_tag)