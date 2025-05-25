from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers.lexicon import LEXICON
from aiogram.types import FSInputFile
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from http_client import api_client

from keyboards.inline import (
    get_main_menu_keyboard,
    get_search_type_keyboard,
    get_pagination_keyboard,
    menu,
)

from http_client import api_client

router = Router()

MOVIES_PER_PAGE = 5


class SearchState(StatesGroup):
    waiting_for_title = State()
    waiting_for_actor = State()
    waiting_for_genre = State()
    waiting_for_director = State()


# === Команда /start ===
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = get_search_type_keyboard()
    photo = FSInputFile("src\images\welcome.png")
    await message.answer_photo(
        photo=photo,
        caption=LEXICON["start"].format(username=message.from_user.first_name),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


RATE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="😍"),
            KeyboardButton(text="😏"),
            KeyboardButton(text="😐"),
            KeyboardButton(text="😒"),
            KeyboardButton(text="🤮🤢💩"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

# Сопоставление эмодзи с числовой оценкой
RATING_MAP = {"😍": 5, "😏": 4, "😐": 3, "😒": 2, "🤮🤢💩": 1}


@router.callback_query(F.data.startswith("rate_"))
async def rate_callback(callback: types.CallbackQuery, state: FSMContext):
    movie_id = int(callback.data.split("_")[1])
    print(movie_id)
    await state.update_data(movie_id=movie_id)

    await callback.message.answer(
        "Оцените фильм:", reply_markup=RATE_KEYBOARD  # тут твоя клавиатура с оценками
    )
    await callback.answer()


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
        result = await api_client.send_rating(
            tg_id=tg_id, movie_id=movie_id, rating=rating
        )
        await message.answer("Спасибо за оценку!", reply_markup=menu())
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


# Команда и коллбек \search
async def show_search_keyboard(target, state: FSMContext):
    keyboard = get_main_menu_keyboard()

    if isinstance(target, types.Message):
        await target.answer(LEXICON["search"], reply_markup=keyboard, parse_mode="HTML")
    elif isinstance(target, types.CallbackQuery):
        await target.message.answer(
            LEXICON["search"], reply_markup=keyboard, parse_mode="HTML"
        )
        await target.answer()
    await state.clear()


# Обработчик на callback "search"
@router.callback_query(lambda c: c.data == "search")
async def cmd_search_callback(callback: types.CallbackQuery, state: FSMContext):
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Начать взаимодействие с ботом\n"
        "/rate — Оценить текущий фильм\n"
        "/history — Посмотреть историю своих оценок\n"
        "/help — Показать это меню"
    )
    await callback.message.answer(help_text, parse_mode="HTML")


# Обработчик на команду /search
@router.message(Command(commands=["search"]))
async def cmd_search_command(message: types.Message, state: FSMContext):
    await show_search_keyboard(message, state)


# === Callback выбора типа поиска ===
@router.callback_query(lambda c: c.data in ["title", "actor", "genre", "director"])
async def handle_search_type(callback: types.CallbackQuery, state: FSMContext):
    mapping = {
        "title": ("Введите название фильма:", SearchState.waiting_for_title),
        "actor": ("Введите имя актёра:", SearchState.waiting_for_actor),
        "genre": ("Введите жанр:", SearchState.waiting_for_genre),
        "director": ("Введите имя режиссёра:", SearchState.waiting_for_director),
    }

    text, target_state = mapping[callback.data]

    # сохраняем тип поиска
    await state.update_data(search_type=callback.data)
    await state.set_state(target_state)

    # await api_client.search_movie()
    print(target_state)
    await callback.message.answer(text)
    await callback.answer()


@router.message(
    StateFilter(
        SearchState.waiting_for_title,
        SearchState.waiting_for_actor,
        SearchState.waiting_for_genre,
        SearchState.waiting_for_director,
    )
)
async def process_search_input(message: types.Message, state: FSMContext):
    user_input = message.text
    data = await state.get_data()
    search_type = data.get("search_type")  # 'title', 'actor', 'genre', 'director'
    # Подготовим аргументы для вызова search_movie
    params = {}

    params[search_type] = user_input
    print(params)

    # Вызов search-функции
    try:
        result = await api_client.search_movie(**params)
        print(result)
    except Exception as e:
        await message.answer("Ошибка при поиске. Попробуйте позже.")
        await state.clear()
        raise

    # Обработка результата
    if not result:
        await message.answer("Ничего не найдено.")
        return

    # Сохраняем результат поиска в состояние
    await state.update_data(search_result=result)

    # Отправляем первый фильм
    page = result["pagination"]["page"]
    limit = result["pagination"]["limit"]
    total_movies = result["totalMovies"]
    # total_pages = (total_movies + limit - 1) // limit

    movie = result["movies"][0]  # Первый фильм
    print(movie)

    description = ""
    if movie.get("description"):
        description = movie["description"]
    if len(description) > 500:
        description = description[:497] + "..."

    year = movie["year"] if movie["year"] else ""

    print(page)
    caption = LEXICON["movie_card"].format(
        title=movie["title"],
        year=year,
        stars=round(movie["rating"]) // 2 * "⭐️",
        rating=round(movie["rating"], 2),
        director=movie["director"],
        actors=", ".join(movie["actors"]),
        genres=", ".join(movie["genres"]),
        description=description,
    )
    keyboard = get_pagination_keyboard(page, limit, movie_id=movie["movieId"])

    await message.answer_photo(
        photo=movie["poster_url"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    # await state.clear()


# ++++++++++++++++++++++++++++
@router.callback_query(F.data.startswith("page_"))
async def page_callback(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[1])
    print(page)
    # Получаем сохранённый результат поиска из FSM-состояния
    data = await state.get_data()
    result = data.get("search_result")

    if not result:
        await callback.answer("Результаты не найдены", show_alert=True)
        return

    movies = result["movies"]
    total_movies = result["totalMovies"]
    page_size = result["pagination"]["limit"]

    movie = movies[page - 1]

    keyboard = get_pagination_keyboard(
        page, total_pages=page_size, movie_id=movie["movieId"]
    )

    description = ""
    if movie.get("description"):
        description = movie["description"]
    if len(description) > 500:
        description = description[:497] + "..."

    year = movie["year"] if movie["year"] else ""

    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=movie["poster_url"],
            caption=LEXICON["movie_card"].format(
                title=movie["title"],
                year=year,
                stars=round(movie["rating"]) // 2 * "⭐️",
                rating=round(movie["rating"], 2),
                director=movie["director"],
                actors=", ".join(movie["actors"]),
                genres=", ".join(movie["genres"]),
                description=description,
            ),
            parse_mode="HTML",
        ),
        reply_markup=keyboard,
    )
    await callback.answer()


# +++++++++++++++++++++++++++

# === Поиск по названию фильма ===
"""@router.message(SearchState.waiting_for_title)
async def handle_movie_search(message: types.Message, state: FSMContext):
    title = message.text.strip()
    results = search_by_name(title)

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

    await state.clear()"""
