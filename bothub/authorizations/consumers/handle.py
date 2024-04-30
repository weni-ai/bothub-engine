from amqp.channel import Channel

from bothub.authorizations.consumers.authorizations_consumer import OrgAuthConsumer



def handle_consumers(channel: Channel) -> None:
    channel.basic_consume("artificial-intelligence.authorizations", callback=OrgAuthConsumer().handle)
