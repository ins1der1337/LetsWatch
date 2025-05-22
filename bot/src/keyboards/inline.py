from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск фильмов", callback_data="search")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    ])
    return keyboard

def get_search_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 По актёру", callback_data="actor"),
            InlineKeyboardButton(text="🎞️ По фильму", callback_data="movie"),
        ],
        [
            InlineKeyboardButton(text="🎭 По жанру", callback_data="genre"),
            InlineKeyboardButton(text="🎥 По режисёру", callback_data="director"),
        ]
    ])
    return keyboard
