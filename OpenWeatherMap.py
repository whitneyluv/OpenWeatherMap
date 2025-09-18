import telegram
from telegram.ext import Updater, CommandHandler
import requests
from datetime import datetime
import sqlite3
import logging
from config import Config

def create_users_table():
    conn = sqlite3.connect(Config.DATABASE_NAME)
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
    conn = sqlite3.connect(Config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username, is_registered) VALUES (?, ?, 1)', (user_id, username))
    conn.commit()
    conn.close()

def check_registration(user_id):
    conn = sqlite3.connect(Config.DATABASE_NAME)
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
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /weather Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        temperature = int(data['main']['temp'])
        description = data['weather'][0]['description']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f'Текущая погода в городе {city}:\n'
        message += f'{current_time}: {temperature}°C, {description}'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе погоды: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных о погоде. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def forecast(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /forecast Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/forecast?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != '200':
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        forecast_data = data['list'][:8]  # Ограничиваем до 8 записей (24 часа)
        
        forecast_message = f'Прогноз погоды в городе {city}:\n'
        for forecast in forecast_data:
            forecast_time = datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d %H:%M:%S')
            temperature = int(forecast['main']['temp'])
            description = forecast['weather'][0]['description']
            forecast_message += f'{forecast_time}: {temperature}°C, {description}\n'
        
        context.bot.send_message(chat_id=chat_id, text=forecast_message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе прогноза: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении прогноза погоды. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def sunrise(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /sunrise Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
        
        message = f'Время восхода солнца в городе {city}:\n'
        message += f'{sunrise_time}'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе времени восхода: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def sunset(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /sunset Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')
        
        message = f'Время захода солнца в городе {city}:\n'
        message += f'{sunset_time}'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе времени заката: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def humidity(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /humidity Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        humidity = data['main']['humidity']
        
        message = f'Уровень влажности в городе {city}:\n'
        message += f'{humidity}%'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе влажности: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def wind(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /wind Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        wind_speed = data['wind']['speed']
        wind_direction = data['wind'].get('deg', 'неизвестно')
        
        message = f'Скорость ветра в городе {city}:\n'
        message += f'{wind_speed} м/с, направление: {wind_direction}°'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе данных о ветре: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

def pressure(update, context):
    chat_id = update.effective_chat.id
    
    if not context.args:
        context.bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите название города. Пример: /pressure Москва')
        return
    
    city = ' '.join(context.args)
    
    try:
        url = f'{Config.OPENWEATHER_BASE_URL}/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units={Config.WEATHER_UNITS}&lang={Config.WEATHER_LANG}'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            context.bot.send_message(chat_id=chat_id, text=f'Город "{city}" не найден. Проверьте правильность написания.')
            return
        
        pressure = data['main']['pressure']
        
        message = f'Атмосферное давление в городе {city}:\n'
        message += f'{pressure} гПа'
        
        context.bot.send_message(chat_id=chat_id, text=message)
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка при запросе давления: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при получении данных. Попробуйте позже.')
    except KeyError as e:
        logging.error(f'Ошибка в структуре данных API: {e}')
        context.bot.send_message(chat_id=chat_id, text='Получены некорректные данные от сервиса погоды.')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
        context.bot.send_message(chat_id=chat_id, text='Произошла неожиданная ошибка.')

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
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    try:
        # Проверяем конфигурацию
        Config.validate_config()
        
        updater = Updater(token=Config.TELEGRAM_BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Добавляем обработчики команд
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('weather', weather))
        dispatcher.add_handler(CommandHandler('forecast', forecast))
        dispatcher.add_handler(CommandHandler('sunrise', sunrise))
        dispatcher.add_handler(CommandHandler('sunset', sunset))
        dispatcher.add_handler(CommandHandler('humidity', humidity))
        dispatcher.add_handler(CommandHandler('wind', wind))
        dispatcher.add_handler(CommandHandler('pressure', pressure))
        dispatcher.add_handler(CommandHandler('help', help))
        
        # Добавляем обработчик ошибок
        dispatcher.add_error_handler(error)
        
        logging.info('Бот запущен и готов к работе!')
        updater.start_polling()
        updater.idle()
        
    except ValueError as e:
        logging.error(f'Ошибка конфигурации: {e}')
        print(f'Ошибка конфигурации: {e}')
    except Exception as e:
        logging.error(f'Критическая ошибка при запуске бота: {e}')
        print(f'Критическая ошибка при запуске бота: {e}')

if __name__ == '__main__':
    try:
        create_users_table()
        main()
    except KeyboardInterrupt:
        logging.info('Бот остановлен пользователем')
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')