import asyncio
import logging
from urllib.parse import urlparse, parse_qs
import redis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import KeyBuilder, StorageKey

from core import AppState


async def rediswatcher(bot: Bot, dp: Dispatcher, connection_string: str):
    """
    Monitors Redis(db-2s) for expired keys(timers), switches state to AppState.Menu, and send message to user
    """
    r = None
    db_num = int(parse_qs(urlparse(connection_string).query).get('db', [0])[0])
    try:
        r = redis.asyncio.Redis.from_url(connection_string)

        await r.config_set("notify-keyspace-events", "KEx")  # key events(K E), which are expired events (e)
        pubsub = r.pubsub()
        await pubsub.psubscribe(f'__keyevent@{db_num}__:expired')
        while True:
            msg = await pubsub.get_message(timeout=0.01)
            if msg and msg['type'] == 'pmessage':
                user_id = int(msg['data'])

                await bot.send_message(user_id, "Timer ended!")
                await dp.storage.set_state(StorageKey(bot.id, user_id, user_id), AppState.Menu)
                # TODO: set user progress, + switch to next state(?)
    except Exception as e:
        logging.warning(e)
        raise e
    finally:
        logging.warning("Redis listener closed")
        await r.aclose()
