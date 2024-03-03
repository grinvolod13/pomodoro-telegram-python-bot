import asyncio
from typing import Coroutine
import logging
from aiogram import Bot, Dispatcher, F, types, filters, methods
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import MagicData
from dotenv import dotenv_values

ENV: dict = dotenv_values()
token: str = ENV['token']
dp = Dispatcher()

##############################################
#    some resouses, TODO: move some in other place
START_TEXT = """Hello, this is Pomodoro bot. Opening soon!
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
        .button(text='🤏 Take a Short Break 🤏') \
        .button(text='🏝️ Take a Long Break 🏝️') \
        .adjust(1, 2)


class AppState(StatesGroup):
    Menu = State()
    Work = State()
    ShortBreak = State()
    LongBreak = State()


async def switch_timer(nextState: str | State | None, user_id: int) -> bool:
    # TODO: stop timer + start needed
    return False


async def pause_timer(user_id: int):
    # TODO: pause timer
    logging.debug("timer paused controller")
    ...


async def continue_timer(user_id: int):
    # TODO: continue timer
    ...


async def check_timer(user_id: int):
    # TODO: check timer
    ...


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
    await switch_timer(AppState.Work, msg.from_user.id)
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="🍅 Pomodoro Started! 🍅",
        reply_markup=Keyboard.pause_inline.as_markup(),
    ))


@dp.message(F.text == '🤏 Take a Short Break 🤏')
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
    await switch_timer(AppState.ShortBreak, msg.from_user.id)
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="🤏 Short Break Started! 🤏",
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
    await switch_timer(AppState.LongBreak, msg.from_user.id)
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
        text=f"{await check_timer(cb.from_user.id)} minutes left",  # TODO: get timer value
    ))
    ...


@dp.callback_query(F.data == 'stop')
async def stop_timer_callback(cb: types.CallbackQuery, bot: Bot, state: FSMContext):
    await switch_timer(AppState.Menu, cb.from_user.id)
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
    bot = Bot(token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
