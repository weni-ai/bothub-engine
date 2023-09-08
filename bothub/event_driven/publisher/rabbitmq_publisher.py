import amqp
import json
from time import sleep

from typing import Dict

from django.conf import settings

from bothub.event_driven.connection.rabbitmq_connection import RabbitMQConnection

class RabbitMQPublisher:

    def __init__(self) -> None:
        self.rabbitmq_connection = RabbitMQConnection()

    def send_message(self, body: Dict, exchange: str, routing_key: str):
        sended = False
        while not sended:
            try:
                self.rabbitmq_connection.channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body
                )
            except Exception as err:
                print(f"error: {err}")
                self.rabbitmq_connection.make_connection()
            sleep(settings.EDA_WAIT_TIME_RETRY)