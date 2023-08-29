from amqp.channel import Channel

from .consumers import ProjectConsumer


def handle_consumers(channel: Channel) -> None:
    channel.basic_consume("project", callback=ProjectConsumer().handle)