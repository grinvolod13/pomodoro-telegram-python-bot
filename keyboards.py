from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


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