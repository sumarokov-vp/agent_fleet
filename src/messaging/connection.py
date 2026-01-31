from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection


class RabbitMQConnection:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection: AbstractRobustConnection | None = None

    async def connect(self) -> AbstractRobustConnection:
        self._connection = await connect_robust(self._url)
        return self._connection

    async def get_channel(self) -> AbstractChannel:
        if not self._connection:
            await self.connect()
        if not self._connection:
            raise RuntimeError("Failed to establish RabbitMQ connection")
        return await self._connection.channel()

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
