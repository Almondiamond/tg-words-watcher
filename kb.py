from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

menu = [
    [InlineKeyboardButton(text="📝 Список слов", callback_data="words_list")],
    [InlineKeyboardButton(text="🖼 Убрать слово", callback_data="words_delete")],
    [InlineKeyboardButton(text="💳 Добавить слово", callback_data="words_add")],
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
    ]
)

words_tracking_kb = [
    [InlineKeyboardButton(text="🖼 Убрать слово", callback_data="words_delete")],
    [InlineKeyboardButton(text="💳 Добавить слово", callback_data="words_add")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]

words_tracking = InlineKeyboardMarkup(
    inline_keyboard=words_tracking_kb
)
