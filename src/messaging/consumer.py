from abc import ABC, abstractmethod

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel

from src.messaging.connection import RabbitMQConnection


class MessageConsumer[T: BaseModel](ABC):
    def __init__(
        self,
        connection: RabbitMQConnection,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        prefetch_count: int = 10,
    ) -> None:
        self._connection = connection
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._prefetch_count = prefetch_count

    async def start(self) -> None:
        channel = await self._connection.get_channel()
        await channel.set_qos(prefetch_count=self._prefetch_count)

        queue = await channel.declare_queue(self._queue_name, durable=True)
        exchange = await channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        await queue.bind(exchange, routing_key=self._routing_key)
        await queue.consume(self._process_message)

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            parsed = self._parse_message(message.body)
            await self._handle_message(parsed)

    @abstractmethod
    def _parse_message(self, body: bytes) -> T:
        pass

    @abstractmethod
    async def _handle_message(self, message: T) -> None:
        pass
