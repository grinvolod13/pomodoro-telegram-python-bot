import datetime
from abc import ABC
from datetime import datetime, timedelta, UTC

from redis.asyncio import Redis, from_url


class TimerStorage(ABC):
    def __init__(self, connection_string):
        self.connection_string = connection_string

    async def pause_timer(self, user_id: int):
        ...

    async def continue_timer(self, user_id: int):
        ...

    async def set_timer(self, user_id: int, time: timedelta):
        ...

    async def check_timer(self, user_id: int) -> timedelta:
        ...

    async def stop_timer(self, user_id: int):
        ...

    async def aclose(self):
        ...


class RedisTimerStorage(TimerStorage):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        self.redis: Redis = from_url(self.connection_string)

    async def pause_timer(self, user_id: int):
        exp_at = await self.redis.expiretime(str(user_id))
        if exp_at == -1 or exp_at == -2:
            # if already paused or timer does not exist
            return

        timer = datetime.fromtimestamp(exp_at, UTC) - datetime.now(UTC)

        await self.redis.set(str(user_id), timer.total_seconds(), ex=None)

    async def continue_timer(self, user_id: int):
        timer: bytes | None = await self.redis.get(str(user_id))
        if timer is None or timer == b'0':
            # if already runs or timer does not exist
            return
        timer: timedelta = timedelta(seconds=float(timer))
        await self.redis.set(str(user_id), 0, ex=timer)

    async def set_timer(self, user_id: int, time: timedelta):
        await self.redis.set(str(user_id), 0, ex=time)

    async def check_timer(self, user_id: int) -> timedelta:
        timer = await self.redis.get(str(user_id))
        exp = await self.redis.expiretime(str(user_id))  # TODO: write issue to redis-py (in doc -> int, not awaitable)
        if timer is None:
            return timedelta()
        timer: float = float(timer)
        if timer == 0:
            return datetime.fromtimestamp(exp, UTC) - datetime.now(UTC)
        return timedelta(seconds=timer)

    async def stop_timer(self, user_id: int):
        await self.redis.delete(str(user_id))

    async def aclose(self):
        await self.redis.aclose()
