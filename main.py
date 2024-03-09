import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher, F, types, filters, methods
from aiogram.fsm.storage.redis import RedisStorage as RedisStateStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from dotenv import dotenv_values

from utils import timerstorage
from utils.timerstorage import TimerStorage

from core import AppState
from utils import timerwatcher

ENV: dict = dotenv_values()
TOKEN: str = ENV['TOKEN']
REDIS_STATE_STORAGE_STRING: str = ENV["REDIS_STATE_STORAGE_STRING"]
REDIS_TIMER_STORAGE_STRING: str = ENV["REDIS_TIMER_STORAGE_STRING"]

dp = Dispatcher(storage=RedisStateStorage.from_url(REDIS_STATE_STORAGE_STRING))
##############################################
#    some resouses, TODO: move some in other place
START_TEXT = """Hello, this is Pomodoro bot!
You can check out source code here:
https://github.com/grinvolod13/pomodoro-telegram-python-bot"""


class Keyboard:
    """Class to store keyboards for bot.
    """

    pause_inline = InlineKeyboardBuilder() \
        .button(text='⏸️ Pause', callback_data='pause') \
        .button(text='⏹️ Stop', callback_data='stop') \
        .button(text='⏱️ Check time left', callback_data='check') \
        .adjust(2, 1)

    continue_inline = InlineKeyboardBuilder() \
        .button(text='▶️ Continue', callback_data='continue') \
        .button(text='⏹️ Stop', callback_data='stop') \
        .button(text='⏱️ Check time left', callback_data='check') \
        .adjust(2, 1)

    menu = ReplyKeyboardBuilder() \
        .button(text='🍅 Start Pomodoro 🍅') \
        .button(text='🍹 Take a Short Break 🍹') \
        .button(text='🏝️ Take a Long Break 🏝️') \
        .adjust(1, 2)


async def set_timer(next_state: str | State | None, user_id: int) -> bool:
    # TODO: Set callback
    pc: TimerStorage = dp["TimerStorage"]
    time = 0
    if next_state == AppState.Work:
        time = 25
    elif next_state == AppState.ShortBreak:
        time = 5
    elif next_state == AppState.LongBreak:
        time = 15

    pc.set_timer(user_id, datetime.timedelta(seconds=time))
    return False


async def pause_timer(user_id: int):
    pc: TimerStorage = dp["TimerStorage"]
    pc.pause_timer(user_id)


async def continue_timer(user_id: int):
    pc: TimerStorage = dp["TimerStorage"]
    pc.continue_timer(user_id)


async def stop_timer(user_id: int):
    pc: TimerStorage = dp["TimerStorage"]
    pc.stop_timer(user_id)


async def check_timer(user_id: int):
    pc: TimerStorage = dp["TimerStorage"]
    return pc.check_timer(user_id)


########################################################################################################################
# Handlers of AppState.Menu and None

@dp.message(filters.CommandStart())
async def start(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text=START_TEXT,
        reply_markup=Keyboard.menu.as_markup(),
    ))
    if await state.get_state() is None:
        await state.set_state(AppState.Menu)


@dp.message(F.text == '🍅 Start Pomodoro 🍅')
async def start_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    """
    Menu -> Work state handler
    """
    if await state.get_state() == AppState.Work:
        await bot(methods.SendMessage(
            chat_id=msg.from_user.id,
            text="Already Pomo-doing! Keep Focusing!",
        ))
        return

    await state.set_state(AppState.Work)
    await set_timer(AppState.Work, msg.from_user.id)
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="🍅 Pomodoro Started! 🍅",
        reply_markup=Keyboard.pause_inline.as_markup(),
    ))


@dp.message(F.text == '🍹 Take a Short Break 🍹')
async def start_short_break(msg: types.Message, bot: Bot, state: FSMContext):
    """
    Menu -> ShortBreak state handler
    """
    if await state.get_state() == AppState.ShortBreak:
        await bot(methods.SendMessage(
            chat_id=msg.from_user.id,
            text="Already taking short break! Keep chilling!",
        ))
        return

    await state.set_state(AppState.ShortBreak)
    await set_timer(AppState.ShortBreak, msg.from_user.id)
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="🍹 Short Break Started! 🍹",
        reply_markup=Keyboard.pause_inline.as_markup(),
    ))


@dp.message(F.text == '🏝️ Take a Long Break 🏝️')
async def start_long_break(msg: types.Message, bot: Bot, state: FSMContext):
    """
    Menu -> LongBreak state handler
    """
    if await state.get_state() == AppState.LongBreak:
        await bot(methods.SendMessage(
            chat_id=msg.from_user.id,
            text="Already taking long break! Keep chilling!",
        ))
        return

    await state.set_state(AppState.LongBreak)
    await set_timer(AppState.LongBreak, msg.from_user.id)
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="🏝️ Long Break Started! 🏝️",
        reply_markup=Keyboard.pause_inline.as_markup(),
    ))


########################################################################################################################
# inline events while timer active

@dp.callback_query(F.data == 'pause')
async def pause_timer_callback(cb: types.CallbackQuery, bot: Bot):
    await pause_timer(cb.from_user.id)
    await bot(methods.AnswerCallbackQuery(
        callback_query_id=cb.id,
        text="⏸️ Paused ⏸️",
    ))
    await bot(methods.EditMessageReplyMarkup(
        chat_id=cb.from_user.id,
        inline_message_id=cb.inline_message_id,
        message_id=cb.message.message_id,
        reply_markup=Keyboard.continue_inline.as_markup(),
    ))


@dp.callback_query(F.data == 'continue')
async def continue_timer_callback(cb: types.CallbackQuery, bot: Bot):
    await continue_timer(cb.from_user.id)
    await bot(methods.AnswerCallbackQuery(
        callback_query_id=cb.id,
        text="▶️ Continued ▶️",
    ))
    await bot(methods.EditMessageReplyMarkup(
        chat_id=cb.from_user.id,
        inline_message_id=cb.inline_message_id,
        message_id=cb.message.message_id,
        reply_markup=Keyboard.pause_inline.as_markup(),
    ))
    ...


@dp.callback_query(F.data == 'check')
async def check_timer_callback(cb: types.CallbackQuery, bot: Bot):
    await bot(methods.AnswerCallbackQuery(
        callback_query_id=cb.id,
        text=f"{await check_timer(cb.from_user.id)} left",
    ))
    ...


@dp.callback_query(F.data == 'stop')
async def stop_timer_callback(cb: types.CallbackQuery, bot: Bot, state: FSMContext):
    await stop_timer(cb.from_user.id)
    await state.set_state(AppState.Menu)

    await bot(methods.SendMessage(
        chat_id=cb.from_user.id,
        text="Stopped.",
        reply_to_message_id=cb.message.message_id
    ))
    ...


########################################################################################################################


async def main():
    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(TOKEN)
    dp["TimerStorage"]: TimerStorage = timerstorage.RedisTimerStorage(REDIS_TIMER_STORAGE_STRING)
    async with asyncio.TaskGroup() as tg:
        bot_task = tg.create_task(dp.start_polling(bot))
        watch_timers_task = tg.create_task(
            timerwatcher.rediswatcher(bot, dp, REDIS_TIMER_STORAGE_STRING)
        )


if __name__ == "__main__":
    asyncio.run(main())
