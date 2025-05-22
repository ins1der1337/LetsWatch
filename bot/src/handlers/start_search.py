from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from model.model_search import search_by_name, search_by_actor, recommend_by_title

router = Router()

class SearchState(StatesGroup):
    waiting_for_title = State()
    waiting_for_actor = State()


# === Команда /start ===
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(f"Здравствуйте, {message.from_user.full_name}!\nИспользуйте /search для поиска фильмов.")


# === Команда /search ===
@router.message(Command("search"))
async def cmd_search(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔍 По актёру", callback_data="actor")],
        [types.InlineKeyboardButton(text="🎥 По фильму", callback_data="movie")]
    ])
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


# === Поиск по названию фильма ===
@router.message(SearchState.waiting_for_title)
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

    await state.clear()