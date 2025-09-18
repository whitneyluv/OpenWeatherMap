import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

class Config:
    """Класс для управления конфигурацией приложения"""
    
    # Telegram Bot настройки
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenWeatherMap API настройки
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    OPENWEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5'
    
    # Настройки базы данных
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'users.db')
    
    # Настройки API запросов
    WEATHER_UNITS = 'metric'  # metric, imperial, kelvin
    WEATHER_LANG = 'ru'       # язык ответов API
    
    @classmethod
    def validate_config(cls):
        """Проверяет наличие всех необходимых переменных окружения"""
        required_vars = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('OPENWEATHER_API_KEY', cls.OPENWEATHER_API_KEY)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}\n"
                f"Создайте файл .env на основе .env.example и заполните необходимые значения."
            )
        
        return True
