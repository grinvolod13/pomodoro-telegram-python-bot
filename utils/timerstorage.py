import datetime
from abc import ABC
from datetime import datetime, timedelta, UTC

from redis import Redis, from_url


class TimerStorage(ABC):
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def pause_timer(self, user_id: int):
        ...

    def continue_timer(self, user_id: int):
        ...

    def set_timer(self, user_id: int, time: timedelta):
        ...

    def check_timer(self, user_id: int) -> timedelta:
        ...

    def stop_timer(self, user_id: int):
        ...


class RedisTimerStorage(TimerStorage):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        self.redis: Redis = from_url(self.connection_string)

    def pause_timer(self, user_id: int):
        exp_at = self.redis.expiretime(str(user_id))
        if exp_at == -1 or exp_at == -2:
            # if already paused or timer does not exist
            return

        timer = datetime.fromtimestamp(exp_at, UTC) - datetime.now(UTC)

        self.redis.set(str(user_id), timer.total_seconds(), ex=None)

    def continue_timer(self, user_id: int):
        timer: bytes | None = (self.redis.get(str(user_id)))
        if timer is None or timer == b'0':
            # if already runs or timer does not exist
            return
        timer: timedelta = timedelta(seconds=float(timer))
        self.redis.set(str(user_id), 0, ex=timer)

    def set_timer(self, user_id: int, time: timedelta):
        self.redis.set(str(user_id), 0, ex=time)

    def check_timer(self, user_id: int) -> timedelta:
        timer = self.redis.get(str(user_id))
        exp = self.redis.expiretime(str(user_id))
        if timer is None:
            return timedelta()
        timer: float = float(timer)
        if timer == 0:
            return datetime.fromtimestamp(exp, UTC) - datetime.now(UTC)
        return timedelta(seconds=timer)

    def stop_timer(self, user_id: int):
        self.redis.delete(str(user_id))
