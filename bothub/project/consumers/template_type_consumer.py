import amqp
from sentry_sdk import capture_exception

from bothub.event_driven.parsers import JSONParser
from bothub.event_driven.consumer.consumers import EDAConsumer
from ..usecases.template_type.creation import TemplateTypeCreationUseCase
from ..usecases.template_type.template_type_dto import TemplateTypeDTO


class TemplateTypeConsumer(EDAConsumer):  # pragma: no cover
    def consume(self, message: amqp.Message):
        print(f"[TemplateTypeConsumer] - Consuming a message. Body: {body}")
        try:
            body = JSONParser.parse(message.body)

            template_type_dto = TemplateTypeDTO(
                uuid=body.get("uuid"),
                name=body.get("name"),
                project_uuid=body.get("project_uuid")
            )

            template_type_creation = TemplateTypeCreationUseCase()
            template_type_creation.create_template_type(template_type_dto)

            message.channel.basic_ack(message.delivery_tag)

        except Exception as exception:
            capture_exception(exception)
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            print(f"[TemplateTypeConsumer] - Message rejected by: {exception}")
