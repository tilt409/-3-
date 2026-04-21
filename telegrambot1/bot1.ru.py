import telebot
import webbrowser
from telebot import types
import sqlite3
import requests
import json
from currency_converter import CurrencyConverter
bot = telebot.TeleBot('8379543992:AAG2gq1gLlJZ6Un48PsySISiLkyDAvyFZck')
name  = None
currency = CurrencyConverter()
@bot.message_handler(content_types=['photo', 'audio'])
def get_photo(message):
    bot.reply_to(message, 'Какое красивое, какой голос')


@bot.message_handler(commands=['site', 'wedsite'])
def site(message):
    webbrowser.open('https://dzen.ru/?yredirect=true&clid=2270456&win=548')

@bot.message_handler(commands=['start', 'main', 'hello'])
def main(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton('Привет'))
    markup.add(types.KeyboardButton('Нужна ссылка на гугл'))
    bot.send_message(message.chat.id, f'Приветственное слово, {message.from_user.first_name} {message.from_user.last_name}!', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def on_click(message):
    if message.text == 'Нужна ссылка на гугл':
        bot.send_message(message.chat.id, 'Держите: https://google.com \nЕсли вам нужно ваше id, напишите в чат ID ')


@bot.message_handler(commands=['pic'])
def pic(message):
    file = open('./i.webp', 'rb')
    bot.send_photo(message.chat.id, file)
    #bot.send_audio/send_video(то же самое)

@bot.message_handler(commands=['help'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти в браузер', url='https://google.com')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Удалить предыдущее сообщение', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Помощь оказана', callback_data='good')
    markup.row(btn2, btn3)
    bot.send_message(message.chat.id, '<b>help</b> <em><u>information</u></em>', parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['reg'])
def reg(message):
    conn = sqlite3.connect('users.sql')
    cursor = conn.cursor()
    #cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, 'Сейчас вас зарегистрируем! Введите ваше имя')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()
    conn = sqlite3.connect('users.sql')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cursor.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))

    bot.send_message(message.chat.id, 'Вы зарегестрированы!', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'users')
def users(call):
    conn = sqlite3.connect('users.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users1 = cursor.fetchall()
    info = ''
    for el in users1:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n'

    cursor.close()
    conn.close()
    bot.send_message(call.message.chat.id, info)

API = '1d0a3ff5985ba17a02724da0747f848e'
# Обработчик команды /weather
@bot.message_handler(commands=['weather'])
def weather_command(message):
    # Отправляем запрос на название города
    sent = bot.send_message(message.chat.id, 'Напиши название города')
    # Регистрируем следующий шаг - ожидание города
    bot.register_next_step_handler(sent, get_weather)


# Обработчик для получения погоды
def get_weather(message):
    city = message.text.strip().lower()
    try:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')

        if res.status_code == 200:
            data = res.json()
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description']

            # Формируем ответ
            reply = (f"Погода в {city.capitalize()}:\n"
                     f"Температура: {temp}°C\n")

            bot.reply_to(message, reply)

            # Отправляем соответствующее изображение
            image = '132.jpg' if temp > 20.0 else '135.jpg'
            with open(image, 'rb') as file:
                bot.send_photo(message.chat.id, file)
        else:
            bot.reply_to(message, 'Город указан неверно или сервис недоступен')

    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {str(e)}')

amonnt = 0
user_data = {}


# Обработчик команды /convert
@bot.message_handler(commands=['convert'])
def convert_command(message):
    sent = bot.send_message(message.chat.id, 'Введите сумму для конвертации')
    bot.register_next_step_handler(sent, process_amount)


def process_amount(message):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError

        # Сохраняем сумму в словаре user_data
        user_data[message.chat.id] = {'amount': amount}

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='convert_usd_eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='convert_eur_usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='convert_usd_gbp')
        btn4 = types.InlineKeyboardButton('Другая валюта', callback_data='convert_custom')
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(message.chat.id, 'Выберите пару валют:', reply_markup=markup)

    except ValueError:
        msg = bot.send_message(message.chat.id, 'Неверный формат. Введите положительное число:')
        bot.register_next_step_handler(msg, process_amount)


# Обработчик callback для конвертации
@bot.callback_query_handler(func=lambda call: call.data.startswith('convert_'))
def convert_callback(call):
    chat_id = call.message.chat.id

    if call.data == 'convert_custom':
        msg = bot.send_message(chat_id, 'Введите пару валют через слэш (например: USD/EUR):')
        bot.register_next_step_handler(msg, process_custom_conversion)
    else:
        # Извлекаем валюты из callback_data (convert_usd_eur -> USD/EUR)
        pair = call.data.replace('convert_', '').replace('_', '/').upper()
        from_curr, to_curr = pair.split('/')

        if chat_id in user_data:
            amount = user_data[chat_id]['amount']
            try:
                result = currency.convert(amount, from_curr, to_curr)
                bot.send_message(chat_id,
                                 f"Результат: {amount} {from_curr} = {round(result, 2)} {to_curr}\n"
                                 f"Для нового расчета введите /convert")
            except Exception as e:
                bot.send_message(chat_id, f"Ошибка конвертации: {str(e)}")


def process_custom_conversion(message):
    chat_id = message.chat.id
    try:
        if chat_id not in user_data:
            bot.send_message(chat_id, "Сначала введите сумму через /convert")
            return

        amount = user_data[chat_id]['amount']
        currencies = message.text.upper().split('/')

        if len(currencies) != 2:
            raise ValueError

        from_curr, to_curr = currencies
        result = currency.convert(amount, from_curr, to_curr)

        bot.send_message(chat_id,
                         f"Результат: {amount} {from_curr} = {round(result, 2)} {to_curr}\n"
                         f"Для нового расчета введите /convert")

    except Exception as e:
        msg = bot.send_message(chat_id, "Неверный формат. Введите пару валют через слэш (например: USD/RUB):")
        bot.register_next_step_handler(msg, process_custom_conversion)

@bot.message_handler()
def info(message):
    if message.text.lower() == 'привет':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Перейти в браузер', url='https://google.com'))
        markup.add(types.InlineKeyboardButton('Удалить предыдущее сообщение', callback_data='delete'))
        markup.add(types.InlineKeyboardButton('Изменить текст', callback_data='edit'))
        bot.send_message(message.chat.id,f'Приветственное слово ✌️, {message.from_user.first_name} {message.from_user.last_name}!', reply_markup=markup)
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}') #либо через elif и команды

@bot.callback_query_handler(func=lambda callback: callback.data in ['delete', 'edit', 'good'])
def callback(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Доброго времени суток', callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'good':
        bot.edit_message_text('Рад помочь!', callback.message.chat.id, callback.message.message_id)


bot.polling(none_stop=True)
