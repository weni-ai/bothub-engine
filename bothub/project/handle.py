from amqp.channel import Channel

from .consumers.project_consumer import ProjectConsumer


def handle_consumers(channel: Channel) -> None:
    channel.basic_consume("projects.artificial-intelligence", callback=ProjectConsumer().handle)
