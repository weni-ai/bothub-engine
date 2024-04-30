from amqp.channel import Channel

from bothub.project.handle import handle_consumers as project_handle_consumers
from bothub.authorizations.consumers.handle import handle_consumers as authorizations_consumers

def handle_consumers(channel: Channel) -> None:
    project_handle_consumers(channel)
    authorizations_consumers(channel)
