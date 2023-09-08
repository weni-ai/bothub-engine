import time

import amqp

from bothub.event_driven.connection.rabbitmq_connection import RabbitMQConnection


class PyAMQPConnectionBackend:
    _start_message = "[+] Connection established. Waiting for events"

    def __init__(self, handle_consumers: callable):
        self._handle_consumers = handle_consumers
        self.rabbitmq_instance = RabbitMQConnection()

    def _drain_events(self, connection: amqp.connection.Connection):
        while True:
            connection.drain_events()

    def start_consuming(self):
        while True:
            try:
                channel = self.rabbitmq_instance.connection.channel()

                self._handle_consumers(channel)

                print(self._start_message)

                self._drain_events(self.rabbitmq_instance.connection)

            except (amqp.exceptions.AMQPError, ConnectionRefusedError, OSError) as error:
                print(f"[-] Connection error: {error}")
                print("    [+] Reconnecting in 5 seconds...")
                time.sleep(5)

            except Exception as error:
                # TODO: Handle exceptions with RabbitMQ
                print("error on drain_events:", type(error), error)
                time.sleep(5)