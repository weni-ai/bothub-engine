import amqp

from bothub.event_driven.parsers import JSONParser
from bothub.event_driven.consumer.consumers import EDAConsumer
from ..usecases.template_type.creation import TemplateTypeCreationUseCase
from ..usecases.template_type.template_type_dto import TemplateTypeDTO


class TemplateTypeConsumer(EDAConsumer):  # pragma: no cover
    def consume(self, message: amqp.Message):
        body = JSONParser.parse(message.body)

        print(f"[TemplateTypeConsumer] - Consuming a message. Body: {body}")

        template_type_dto = TemplateTypeDTO(uuid=body.get("uuid"), name=body.get("name"), project_uuid=body.get("project_uuid"))

        template_type_creation = TemplateTypeCreationUseCase()
        template_type_creation.create_template_type(template_type_dto)

        message.channel.basic_ack(message.delivery_tag)
