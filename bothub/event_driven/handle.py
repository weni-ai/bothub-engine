from amqp.channel import Channel

from bothub.project.handle import handle_consumers as project_handle_consumers

def handle_consumers(channel: Channel) -> None:
    project_handle_consumers(channel)