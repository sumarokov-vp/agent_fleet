import aio_pika
import pika
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


class SyncMessagePublisher:
    def __init__(self, rabbitmq_url: str, exchange_name: str) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._exchange_name = exchange_name

    def publish(self, message: BaseModel, routing_key: str) -> None:
        params = pika.URLParameters(self._rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type="topic",
            durable=True,
        )
        channel.basic_publish(
            exchange=self._exchange_name,
            routing_key=routing_key,
            body=message.model_dump_json().encode(),
            properties=pika.BasicProperties(content_type="application/json"),
        )
        connection.close()
