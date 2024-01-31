import telegram
from telegram.ext import Updater, CommandHandler
import requests
from datetime import datetime
import sqlite3

def create_users_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_registered INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username, is_registered) VALUES (?, ?, 1)', (user_id, username))
    conn.commit()
    conn.close()

def check_registration(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_registered FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def start(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username

    if not check_registration(user_id):
        register_user(user_id, username)
        message = f"Привет, {username}! Вы успешно зарегистрированы. Введите команду /help, чтобы получить список доступных команд."
    else:
        message = f"С возвращением, {username}! Введите команду /help, чтобы получить список доступных команд."

    context.bot.send_message(chat_id=chat_id, text=message)

def weather(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    temperature = int(data['main']['temp'])
    description = data['weather'][0]['description']

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f'Текущая погода в городе {city}:\n'
    message += f'{current_time}: {temperature}°C, {description}'

    context.bot.send_message(chat_id=chat_id, text=message)

def forecast(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    forecast_data = data['list']

    forecast_message = f'Прогноз погоды в городе {city}:\n'
    for forecast in forecast_data:
        forecast_time = datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d %H:%M:%S')
        temperature = int(forecast['main']['temp'])
        description = forecast['weather'][0]['description']
        forecast_message += f'{forecast_time}: {temperature}°C, {description}\n'

    context.bot.send_message(chat_id=chat_id, text=forecast_message)

def sunrise(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')

    message = f'Время восхода солнца в городе {city}:\n'
    message += f'{sunrise_time}'

    context.bot.send_message(chat_id=chat_id, text=message)

def sunset(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')

    message = f'Время захода солнца в городе {city}:\n'
    message += f'{sunset_time}'

    context.bot.send_message(chat_id=chat_id, text=message)

def humidity(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    humidity = data['main']['humidity']

    message = f'Уровень влажности в городе {city}:\n'
    message += f'{humidity}%'

    context.bot.send_message(chat_id=chat_id, text=message)

def wind(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    wind_speed = data['wind']['speed']
    wind_direction = data['wind']['deg']

    message = f'Скорость ветра в городе {city}:\n'
    message += f'{wind_speed} м/с, направление: {wind_direction}°'

    context.bot.send_message(chat_id=chat_id, text=message)

def pressure(update, context):
    chat_id = update.effective_chat.id
    city = context.args[0]
    api_key = ''

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'

    response = requests.get(url)
    data = response.json()

    pressure = data['main']['pressure']

    message = f'Атмосферное давление в городе {city}:\n'
    message += f'{pressure} гПа'

    context.bot.send_message(chat_id=chat_id, text=message)

def help(update, context):
    chat_id = update.effective_chat.id
    message = '''Доступные команды:
/weather <город> - получить текущую погоду в заданном городе.
/forecast <город> - получить прогноз погоды в заданном городе.
/sunrise <город> - получить время восхода солнца в заданном городе.
/sunset <город> - получить время захода солнца в заданном городе.
/humidity <город> - получить уровень влажности в заданном городе.
/wind <город> - получить текущую скорость ветра в заданном городе.
/pressure <город> - получить текущее атмосферное давление в заданном городе.
/help - получить справку и список доступных команд.'''
    context.bot.send_message(chat_id=chat_id, text=message)

def error(update, context):
    chat_id = update.effective_chat.id
    message = 'Неправильный формат команды. Введите /help, чтобы получить список доступных команд.'
    context.bot.send_message(chat_id=chat_id, text=message)

def main():
    bot_token = ''
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('weather', weather))
    dispatcher.add_handler(CommandHandler('forecast', forecast))
    dispatcher.add_handler(CommandHandler('sunrise', sunrise))
    dispatcher.add_handler(CommandHandler('sunset', sunset))
    dispatcher.add_handler(CommandHandler('humidity', humidity))
    dispatcher.add_handler(CommandHandler('wind', wind))
    dispatcher.add_handler(CommandHandler('pressure', pressure))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('start', help))
    dispatcher.add_handler(CommandHandler('help', help))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    create_users_table()
    main()