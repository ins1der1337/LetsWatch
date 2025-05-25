from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Поиск фильмов", callback_data="search")]
        ]
    )
    return keyboard


def get_search_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 По актёру", callback_data="actor"),
                InlineKeyboardButton(text="🎞️ По фильму", callback_data="movie"),
            ],
            [
                InlineKeyboardButton(text="🎭 По жанру", callback_data="genre"),
                InlineKeyboardButton(text="🎥 По режисёру", callback_data="director"),
            ],
        ]
    )
    return keyboard


def get_pagination_keyboard(current_page, total_pages=5, movie_id=1):
    buttons = []
    if current_page >= 1:
        buttons.append(
            InlineKeyboardButton(
                text="◀️ Назад", callback_data=f"page_{current_page - 1}"
            )
        )
    if current_page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Вперед ▶️", callback_data=f"page_{current_page + 1}"
            )
        )

    # Первый ряд — кнопки "Назад" и "Вперед"
    keyboard = [buttons] if buttons else []

    # Второй ряд — кнопка "Меню" по центру
    keyboard.append(
        [
            InlineKeyboardButton(text="🏠 Меню", callback_data="search",),
            InlineKeyboardButton(text="⭐ Оценить", callback_data=f"rate_{movie_id}",),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🏠 Меню", callback_data="search")]]
    )
    return keyboard
