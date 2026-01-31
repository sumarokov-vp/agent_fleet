import aio_pika
from pydantic import BaseModel

from src.messaging.connection import RabbitMQConnection


class MessagePublisher:
    def __init__(self, connection: RabbitMQConnection, exchange_name: str) -> None:
        self._connection = connection
        self._exchange_name = exchange_name

    async def publish(self, message: BaseModel, routing_key: str) -> None:
        channel = await self._connection.get_channel()
        exchange = await channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        await exchange.publish(
            aio_pika.Message(
                body=message.model_dump_json().encode(),
                content_type="application/json",
            ),
            routing_key=routing_key,
        )
