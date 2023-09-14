from abc import ABC, abstractmethod

import amqp

from bothub.event_driven.signals import message_started, message_finished


class EDAConsumer(ABC):  # pragma: no cover
    def handle(self, message: amqp.Message):
        message_started.send(sender=self)
        try:
            self.consume(message)
        finally:
            message_finished.send(sender=self)

    @abstractmethod
    def consume(self, message: amqp.Message):
        pass
