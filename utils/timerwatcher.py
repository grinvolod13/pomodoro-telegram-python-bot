import asyncio
import logging

import redis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import KeyBuilder, StorageKey

from core import AppState


async def rediswatcher(bot: Bot, dp: Dispatcher):
    """
    Monitors Redis(db-2s) for expired keys(timers), switches state to AppState.Menu, and send message to user
    """
    r = None
    try:
        r = redis.asyncio.Redis.from_url("redis:///127.0.0.1?db=2") # TODO: use from ENV variables

        await r.config_set("notify-keyspace-events", "KEx")  # key events(K E), which are expired events (e)
        pubsub = r.pubsub()
        await pubsub.psubscribe('__keyevent@2__:expired')  # TODO: get db № dynamically from connection_string
        while True:
            msg = await pubsub.get_message(timeout=0.01)
            if msg and msg['type'] == 'pmessage':
                user_id = int(msg['data'])

                await bot.send_message(user_id, "Timer ended.")
                await dp.storage.set_state(StorageKey(bot.id, user_id, user_id), AppState.Menu)  # TODO: retrive and set
                # correct state
    except Exception as e:
        logging.warning(e)
        raise e
    finally:
        logging.warning("Redis listener closed")
        await r.aclose()
