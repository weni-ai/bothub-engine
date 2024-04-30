import amqp
from sentry_sdk import capture_exception

from bothub.event_driven.parsers import JSONParser
from bothub.event_driven.consumer.consumers import EDAConsumer
from bothub.authorizations.usecases import AuthorizationsUsecase
from bothub.authorizations.usecases.dto import OrgAuthDTO


class OrgAuthConsumer(EDAConsumer):  # pragma: no cover
    def consume(self, message: amqp.Message):
        print(f"[ProjectConsumer] - Consuming a message. Body: {message.body}")

        try:
            body = JSONParser.parse(message.body)

            action = body.get("action")

            org_auth_dto = OrgAuthDTO(
                user=body.get("user_email"),
                org_id=body.get("organization_intelligence"),
                role=body.get("role")
            )

            usecase = AuthorizationsUsecase()
            usecase.dispatch(action)(org_auth_dto)

            message.channel.basic_ack(message.delivery_tag)

        except Exception as exception:
            capture_exception(exception)
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            print(f"[ProjectConsumer] - Message rejected by: {exception}")
