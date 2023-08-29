import amqp
from sentry_sdk import capture_exception

from ..usecases import (
    ProjectCreationUseCase,
    ProjectCreationDTO,
)

from bothub.event_driven.parsers import JSONParser
from bothub.event_driven.consumers import EDAConsumer


class ProjectConsumer(EDAConsumer):  # pragma: no cover
    def consume(self, message: amqp.Message):
        print(f"[ProjectConsumer] - Consuming a message. Body: {message.body}")

        try:
            body = JSONParser.parse(message.body)

            project_dto = ProjectCreationDTO(
                uuid=body.get("uuid"),
                name=body.get("name"),
                is_template=body.get("is_template"),
                date_format=body.get("date_format"),
                template_type_uuid=body.get("template_type_uuid"),
                timezone=body.get("timezone"),
            )

            project_creation = ProjectCreationUseCase()
            project_creation.create_project(project_dto, body.get("user_email"))

            message.channel.basic_ack(message.delivery_tag)

        except Exception as exception:
            capture_exception(exception)
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            print(f"[ProjectConsumer] - Message rejected by: {exception}")