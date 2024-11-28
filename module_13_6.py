from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
kb.row(button, button2)

in_kb = InlineKeyboardMarkup(resize_keyboard=True)
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
in_kb.add(button3, button4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(text="Привет!")
async def urban_message(message):
    await message.answer('Введите команду /start, чтобы начать общение')


@dp.message_handler(commands=['start'])
async def urban_message(message):
    print("Start")
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=in_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n'
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()


@dp.message_handler(text="Информация")
async def set_gender(message):
    await message.answer(f"Бот, который помогает пользователю рассчитывать норму калорий"
                         f"в зависимости от его пола, возраста, роста и веса")


@dp.callback_query_handler(text='calories')
async def set_gender(call):
    await call.message.answer("Для корректного расчета калорий, укажите свой пол (F/M):")
    await UserState.gender.set()
    await call.answer()


@dp.message_handler(state=UserState.gender)
async def set_age(message, state):
    gender = message.text.upper()
    if gender not in ['F', 'M']:
        await message.answer("Пожалуйста, укажите корректный пол (F/M):")
        return
    await state.update_data(gender=gender)
    await message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    try:
        await state.update_data(age=int(message.text))
        await message.answer(f"Введите свой рост:")
        await UserState.growth.set()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст числом:")


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    try:
        await state.update_data(growth=float(message.text))
        await message.answer(f"Введите свой вес:")
        await UserState.weight.set()
    except ValueError:
        await message.answer(f"Пожалуйста, введите корректный рост числом:")


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight=float(message.text))
        data = await state.get_data()
        if data['gender'] == 'M':
            await message.answer(
                f"Ваша норма калорий {10 * data['weight'] + 6.25 * data['growth'] + 5 * data['age'] + 5}")
            await state.finish()
        else:
            await message.answer(
                f"Ваша норма калорий {10 * data['weight'] + 6.25 * data['growth'] + 5 * data['age'] - 161}")
            await state.finish()
    except ValueError:
        await message.answer(f"Пожалуйста, введите корректный вес числом:")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
