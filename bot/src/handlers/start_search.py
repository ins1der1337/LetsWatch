from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from http_client import api_client


router = Router()

class SearchState(StatesGroup):
    waiting_for_title = State()
    waiting_for_actor = State()


# === Команда /start ===
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="оценить фильм", callback_data="rating")],
    ])
    res = await api_client.register_user(message.from_user.id, message.from_user.username)
    
    await message.answer(f"Здравствуйте, {message.from_user.full_name}!\n оцените фильм.\n {res}", reply_markup=keyboard)

RATE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="😍"),
            KeyboardButton(text="😏"),
            KeyboardButton(text="😐"),
            KeyboardButton(text="😒"),
            KeyboardButton(text="🤮🤢💩")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Сопоставление эмодзи с числовой оценкой
RATING_MAP = {
    "😍": 5,
    "😏": 4,
    "😐": 3,
    "😒": 2,
    "🤮🤢💩": 1
}


@router.message(Command("rate"))
async def cmd_rate(message: types.Message, state: FSMContext):
    # Предположим, что movie_id берётся из контекста или предыдущего действия
    # В реальности ты можешь получать его при показе фильма
    movie_id = 589  # ← замени это на динамическое значение из твоей логики

    await state.update_data(movie_id=movie_id)  # сохраняем в FSM
    await message.answer("Оцените фильм:", reply_markup=RATE_KEYBOARD)


@router.message(lambda msg: msg.text in RATING_MAP.keys())
async def handle_rating(message: types.Message, state: FSMContext):
    rating = RATING_MAP[message.text]
    data = await state.get_data()
    movie_id = data.get("movie_id")
    tg_id = message.from_user.id

    if not movie_id:
        await message.answer("Ошибка: не удалось определить фильм.")
        return

    try:
        result = await api_client.send_rating(tg_id=tg_id, movie_id=movie_id, rating=rating)
        await message.answer("Спасибо за оценку!")
        print("Результат оценки:", result)
    except Exception as e:
        await message.answer("Не удалось сохранить оценку.")
        print("Ошибка при отправке оценки:", e)

    await state.clear()
    
@router.message(Command("history"))
async def cmd_history(message: types.Message):
    tg_id = message.from_user.id

    try:
        response = await api_client.get_user_reviews(tg_id=tg_id)

        if not response or not isinstance(response, dict):
            await message.answer("Вы ещё не оценили ни один фильм.")
            return

        reviews = response.get("reviews", [])
        if not reviews:
            await message.answer("Вы ещё не оценили ни один фильм.")
            return

        text = "🎬 <b>Ваши оценки:</b>\n\n"
        for review in reviews:
            if not isinstance(review, dict):
                print("Некорректный формат записи:", review)
                continue

            rating = review.get("rating", 0)
            movie_id = review.get("movie_id", "Неизвестный ID")

            text += f"🎥 Фильм ID: {movie_id}\n⭐ Оценка: {rating}/5\n\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer("Ошибка при загрузке истории оценок.")
        print("Ошибка при получении истории:", e)
        
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Начать взаимодействие с ботом\n"
        "/rate — Оценить текущий фильм\n"
        "/history — Посмотреть историю своих оценок\n"
        "/help — Показать это меню"
    )
    await message.answer(help_text, parse_mode="HTML")

# === Команда /search ===
@router.message(Command("search"))
async def cmd_search(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text="🔍 По актёру", callback_data="actor")],
            [KeyboardButton(text="🎥 По фильму", callback_data="movie")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True)
    await message.answer("Выберите тип поиска:", reply_markup=keyboard)


# === Callback выбора типа поиска ===
@router.callback_query()
async def process_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "movie":
        await callback.message.answer("Введите название фильма:")
        await state.set_state(SearchState.waiting_for_title)
    elif callback.data == "actor":
        await callback.message.answer("Введите имя актёра:")
        await state.set_state(SearchState.waiting_for_actor)
    await callback.answer()


# # === Поиск по названию фильма ===
# @router.message(SearchState.waiting_for_title)
# async def handle_movie_search(message: types.Message, state: FSMContext):
#     title = message.text.strip()
#     results = search_by_name(title)

#     if results.empty:
#         await message.answer("Фильмы не найдены.")
#     else:
#         for _, row in results.iterrows():
#             text = f"🎬 <b>{row['title']}</b> ({row['year']})\n" \
#                    f"Жанры: {row['genres']}\n" \
#                    f"Рейтинг: ⭐ {row['rating']}"
#             await message.answer(text)

#             # Предложить рекомендации
#             recommendations = recommend_by_title(row['title'])
#             if not recommendations is None:
#                 await message.answer("Попробуйте посмотреть:")
#                 for _, rec in recommendations.iterrows():
#                     await message.answer(f"👉 {rec['title']} — {rec['genres']}")

#     await state.clear()


# # === Поиск по актёру ===
# @router.message(SearchState.waiting_for_actor)
# async def handle_actor_search(message: types.Message, state: FSMContext):
#     actor = message.text.strip()
#     # results = search_by_actor(actor)

#     if results.empty:
#         await message.answer("Фильмы с этим актёром не найдены.")
#     else:
#         for _, row in results.iterrows():
#             text = f"🎬 <b>{row['title']}</b> ({row['year']})\n" \
#                    f"Актёры: {row['actors']}\n" \
#                    f"Рейтинг: ⭐ {row['rating']}"
#             await message.answer(text)

#     await state.clear()