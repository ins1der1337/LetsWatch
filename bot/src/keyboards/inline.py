from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder

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

def get_pagination_keyboard(page: int, TOTAL_PAGES=1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 1:
        builder.button(text="◀️ Назад", callback_data=f"page_{page - 1}")
    if page < TOTAL_PAGES:
        builder.button(text="Вперед ▶️", callback_data=f"page_{page + 1}")
    return builder.as_markup()
