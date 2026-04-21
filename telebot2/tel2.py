from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
bot = Bot("8434844653:AAEy5h7eO_CnKZppS0ZpEEmun5-S7VfGnwo")
dp = Dispatcher()


@dp.message(Command('web'))
async def send_web(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть веб страницу",
                web_app=WebAppInfo(url="https://tilt409.github.io/telebotpril/")
            )]  # Закрывающая квадратная скобка для списка кнопок
        ],  # Закрывающая квадратная скобка для keyboard
        resize_keyboard=True,
        one_time_keyboard=True
    )  # Закрывающая круглая скобка для ReplyKeyboardMarkup

    await message.answer(
        'Привет, друг',
        reply_markup=markup
    )
# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    #await message.answer("Привет!")
    await message.reply('Привет!')
    #file = open('/some.png')
    #await message.answer_photo(file)

@dp.message(Command("reply"))
async def reply(message: types.Message):
    # Создаем Reply-клавиатуру
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Site")],  # Первый ряд с одной кнопкой
            [types.KeyboardButton(text="Website")]  # Второй ряд с одной кнопкой
        ],
        resize_keyboard=True,  # Подгоняем размер клавиатуры
        one_time_keyboard=True  # Скрываем клавиатуру после нажатия
    )
    await message.answer(
        "Выберите вариант:",  # Исправлен текст сообщения (было '<UNK>')
        reply_markup=markup
    )

# Обработчик для кнопок Reply-клавиатуры
@dp.message(lambda message: message.text in ["Site", "Website"])
async def handle_buttons(message: types.Message):
    if message.text == "Site":
        await message.answer("Вы выбрали Site", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Website":
        await message.answer("Вы выбрали Website", reply_markup=types.ReplyKeyboardRemove())

@dp.message()
async def info(message: types.Message):
    # Исправлено создание клавиатуры (используем InlineKeyboardBuilder)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="site", url="https://google.com"))
    builder.add(types.InlineKeyboardButton(text="Hello",callback_data="hello"))
    await message.reply('Hello', reply_markup=builder.as_markup())
@dp.callback_query()
async def callback(call):
    await call.message.answer(call.data)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
