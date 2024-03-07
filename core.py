from aiogram.fsm.state import StatesGroup, State


class AppState(StatesGroup):
    Menu = State()
    Work = State()
    ShortBreak = State()
    LongBreak = State()