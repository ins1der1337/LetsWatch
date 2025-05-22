from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers.lexicon import LEXICON
from aiogram.types import FSInputFile
from aiogram.filters import StateFilter

from keyboards.inline import get_main_menu_keyboard, get_search_type_keyboard, get_pagination_keyboard

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
    photo = FSInputFile('src\images\welcome.png')
    await message.answer_photo(photo=photo, caption=LEXICON['start'].format(username=message.from_user.first_name), \
                               reply_markup=keyboard, parse_mode='HTML')
    

# Команда и коллбек \search
async def show_search_keyboard(target, state: FSMContext):
    keyboard = get_main_menu_keyboard()

    if isinstance(target, types.Message):
        await target.answer(LEXICON['search'], reply_markup=keyboard, parse_mode='HTML')
    elif isinstance(target, types.CallbackQuery):
        await target.message.answer(LEXICON['search'], reply_markup=keyboard, parse_mode='HTML')
        await target.answer()

# Обработчик на callback "search"
@router.callback_query(lambda c: c.data == "search")
async def cmd_search_callback(callback: types.CallbackQuery, state: FSMContext):
    await show_search_keyboard(callback, state)

# Обработчик на команду /search
@router.message(Command(commands=["search"]))
async def cmd_search_command(message: types.Message, state: FSMContext):
    await show_search_keyboard(message, state)


# === Callback выбора типа поиска ===
@router.callback_query(lambda c: c.data in ["movie", "actor", "genre", "director"])
async def handle_search_type(callback: types.CallbackQuery, state: FSMContext):
    mapping = {
        "movie": ("Введите название фильма:", SearchState.waiting_for_title),
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


@router.message(StateFilter(
    SearchState.waiting_for_title,
    SearchState.waiting_for_actor,
    SearchState.waiting_for_genre,
    SearchState.waiting_for_director
))
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
    else:
        await message.answer(str(result))  # ссыль на пагинацию 
        # for movie in result:
        #     # Отправляем краткую инфу по каждому фильму
        #     print("мяу")
        #     title = movie.get("title", "Без названия")
        #     year = movie.get("year", "неизвестен")
        #     await message.answer(f"<b>{title}</b> ({year})", parse_mode='HTML')

    await state.clear()


# ++++++++++++++++++++++++++++
def format_movie(movie: dict) -> str:
    return LEXICON['movie_card']


@router.callback_query(F.data.startswith("page_"))
async def page_callback(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[1])

    # Получаем сохранённый результат поиска из FSM-состояния
    data = await state.get_data()
    result = data.get("search_result")

    if not result:
        await callback.answer("Результаты не найдены", show_alert=True)
        return

    movies = result["movies"]
    total_movies = result["totalMovies"]
    page_size = result["pagination"]["limit"]
    total_pages = (total_movies + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size
    movie = movies[start:end][0]

    def get_keyboard():
        kb = InlineKeyboardBuilder()
        if page > 1:
            kb.button(text="◀️ Назад", callback_data=f"page_{page - 1}")
        if page < total_pages:
            kb.button(text="Вперед ▶️", callback_data=f"page_{page + 1}")
        return kb.as_markup()
# +++++++++++++++++++++++++++

# === Поиск по названию фильма ===
'''@router.message(SearchState.waiting_for_title)
async def handle_movie_search(message: types.Message, state: FSMContext):
    title = message.text.strip()
    results = search_by_name(title)

    if results.empty:
        await message.answer("Фильмы не найдены.")
    else:
        for _, row in results.iterrows():
            text = f"🎬 <b>{row['title']}</b> ({row['year']})\n" \
                   f"Жанры: {row['genres']}\n" \
                   f"Рейтинг: ⭐ {row['rating']}"
            await message.answer(text)

            # Предложить рекомендации
            recommendations = recommend_by_title(row['title'])
            if not recommendations is None:
                await message.answer("Попробуйте посмотреть:")
                for _, rec in recommendations.iterrows():
                    await message.answer(f"👉 {rec['title']} — {rec['genres']}")

    await state.clear()


# === Поиск по актёру ===
@router.message(SearchState.waiting_for_actor)
async def handle_actor_search(message: types.Message, state: FSMContext):
    actor = message.text.strip()
    results = search_by_actor(actor)

    if results.empty:
        await message.answer("Фильмы с этим актёром не найдены.")
    else:
        for _, row in results.iterrows():
            text = f"🎬 <b>{row['title']}</b> ({row['year']})\n" \
                   f"Актёры: {row['actors']}\n" \
                   f"Рейтинг: ⭐ {row['rating']}"
            await message.answer(text)

    await state.clear()'''