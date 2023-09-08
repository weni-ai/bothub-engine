from amqp.channel import Channel

from .consumers.project_consumer import ProjectConsumer
from .consumers.template_type_consumer import TemplateTypeConsumer

def handle_consumers(channel: Channel) -> None:
    channel.basic_consume("artificial-intelligence.projects", callback=ProjectConsumer().handle)
    channel.basic_consume("artificial-intelligence.template-types", callback=TemplateTypeConsumer().handle)
