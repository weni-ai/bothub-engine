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
                    msg=amqp.Message(
                        body=json.dumps(body).encode(),
                        properties={"delivery_mode": 2},
                        content_type="application/octet-stream",
                    )
                )
                sended = True
            except Exception as err:
                print(f"error: {err}")
                self.rabbitmq_connection._establish_connection()
            sleep(settings.EDA_WAIT_TIME_RETRY)