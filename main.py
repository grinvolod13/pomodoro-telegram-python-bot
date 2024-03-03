import asyncio
from aiogram import Bot, Dispatcher, F, types, filters, methods
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import dotenv_values

ENV: dict = dotenv_values()
token: str = ENV['token']

dp = Dispatcher()

##############################################
# some resouses, TODO: move some in other place
START_TEXT = "Hello, this is Pomodoro bot. Opening soon!"


class Keyboard:
    """Class to store keyboards for bot.
        Attributes:
            pause:  layout with pause
            start:  layout with start
            menu:  menu layout
    """

    pause = ReplyKeyboardBuilder() \
        .button(text='⏸️ Pause') \
        .button(text='⏭️ Skip') \
        .button(text='🛑 Menu') \
        .adjust(1, 3)

    start = ReplyKeyboardBuilder() \
        .button(text='▶️ Continue') \
        .button(text='⏭️ Skip') \
        .button(text='🛑 Menu') \
        .adjust(1, 3)

    menu = ReplyKeyboardBuilder() \
        .button(text='🍅 Start! 🍅') \
        .button(text='🤏 Take a Short Break 🤏') \
        .button(text='🏝️ Take a Long Break 🏝️') \
        .adjust(1, 3)


class AppState(StatesGroup):
    Menu = State()
    Work = State()
    ShortBreak = State()
    LongBreak = State()


#########################################

@dp.message(filters.CommandStart())
async def start(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text=START_TEXT,
        reply_markup=Keyboard.menu.as_markup(),

    ))
    if await state.get_state() is None:
        await state.set_state(AppState.Menu)


@dp.message(AppState.Menu, F.text == '🍅 Start! 🍅')
async def start_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    """
    Menu -> Work state handler
    """
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Pomodoro Started!",
        reply_markup=Keyboard.pause.as_markup(),
    ))
    await state.set_state(AppState.Work)
    # TODO: launch timer amd make timer callback


########################################################################################################################
# Handlers of AppState.Work messages

@dp.message(AppState.Work, F.text == '⏸️ Pause')
async def pause_pomodoro(msg: types.Message, bot: Bot):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Paused",
        reply_markup=Keyboard.start.as_markup(),
    ))
    # TODO: Make timer stop
    ...


@dp.message(AppState.Work, F.text == '▶️ Continue')
async def continue_pomodoro(msg: types.Message, bot: Bot):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Continued.",
        reply_markup=Keyboard.pause.as_markup(),
    ))
    # TODO: Make timer continue
    ...


@dp.message(AppState.Work, F.text == '⏭️ Skip')
async def skip_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Skipped. Take your short brake!",
        reply_markup=Keyboard.pause.as_markup(),
    ))
    # TODO: remove work timer, start short break timer
    await state.set_state(AppState.ShortBreak)
    # TODO: depends on user's cycle state, make short or large break
    ...


@dp.message(AppState.Work, F.text == '🛑 Menu')
async def skip_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Pomodoro cycle stopped",
        reply_markup=Keyboard.menu.as_markup(),
    ))
    # TODO: remove work timer
    # TODO: show user stats
    await state.set_state(AppState.Menu)
    ...


########################################################################################################################
# Handlers of AppState.ShortBreak messages


@dp.message(AppState.ShortBreak, F.text == '⏸️ Pause')
async def pause_short_break(msg: types.Message, bot: Bot):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Paused",
        reply_markup=Keyboard.start.as_markup(),
    ))
    # TODO: Make short break timer stop
    ...


@dp.message(AppState.ShortBreak, F.text == '▶️ Continue')
async def continue_pomodoro(msg: types.Message, bot: Bot):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Continued.",
        reply_markup=Keyboard.pause.as_markup(),
    ))
    # TODO: Make short break timer continue
    ...


@dp.message(AppState.ShortBreak, F.text == '⏭️ Skip')
async def skip_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Focus on your task!",
        reply_markup=Keyboard.pause.as_markup(),
    ))
    # TODO: remove short break timer, start work timer
    await state.set_state(AppState.Work)
    # TODO: track user's work cycle
    ...


@dp.message(AppState.ShortBreak, F.text == '🛑 Menu')
async def skip_pomodoro(msg: types.Message, bot: Bot, state: FSMContext):
    await bot(methods.SendMessage(
        chat_id=msg.from_user.id,
        text="Pomodoro cycle stopped",
        reply_markup=Keyboard.menu.as_markup(),
    ))
    # TODO: remove short break timer
    # TODO: show user stats
    await state.set_state(AppState.Menu)
    ...


########################################################################################################################


async def main():
    bot = Bot(token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
