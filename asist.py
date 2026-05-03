# asist.py
# Текстовый ассистент Дилл

import datetime
import pywhatkit
import wikipediaapi
from upgrades import WeatherNoAPI, TextInterface

# Создаём экземпляры модулей
weather = WeatherNoAPI()
ui = TextInterface()


class SmartAssistant:
    """
    Текстовый ассистент.
    Принимает команды текстом и отвечает текстом.
    """
    
    def __init__(self, name="Ассистент"):
        self.name = name
        self.running = False
        
        # Словарь команд и ключевых слов
        self.commands = {
            'greeting': ['привет', 'здравствуй', 'добрый день', 'доброе утро', 
                        'добрый вечер', 'приветствую'],
            'goodbye': ['пока', 'до свидания', 'выключись', 'выход', 'стоп', 'exit', 'quit'],
            'time': ['время', 'который час', 'сколько времени', 'подскажи время', 'часы'],
            'weather': ['погода', 'какая погода', 'температура', 'сколько градусов', 'прогноз'],
            'search': ['найди', 'поищи', 'что такое', 'кто такой', 'расскажи про', 'узнай'],
            'video': ['включи видео', 'найди видео', 'покажи видео', 'ютуб', 'youtube'],
            'help': ['помощь', 'команды', 'что ты умеешь', 'help', 'хелп']
        }
        
        print(f"✅ Ассистент {self.name} инициализирован")
    
    def analyze_command(self, text):
        """
        Анализирует текст и определяет, что хочет пользователь.
        Возвращает (намерение, дополнительный текст)
        """
        if not text:
            return 'empty', None
        
        # Проверяем каждую группу команд
        for intent, phrases in self.commands.items():
            for phrase in phrases:
                if phrase in text:
                    # Для поиска — извлекаем запрос после ключевого слова
                    if intent == 'search':
                        for p in ['найди', 'поищи', 'что такое', 'кто такой', 'расскажи про', 'узнай']:
                            if p in text:
                                query = text.split(p, 1)[-1].strip()
                                if query:
                                    return 'search', query
                        return 'search', text
                    
                    # Для видео — извлекаем название
                    elif intent == 'video':
                        for p in ['включи видео', 'найди видео', 'покажи видео', 'ютуб', 'youtube']:
                            if p in text:
                                query = text.replace(p, '').strip()
                                if query:
                                    return 'video', query
                        return 'video', ''
                    
                    # Для погоды — может содержать город
                    elif intent == 'weather':
                        return 'weather', text
                    
                    # Остальные команды
                    else:
                        return intent, text
        
        # Если ничего не найдено
        return 'unknown', text
    
    def get_time(self):
        """Получить текущее время в красивом формате"""
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
        # Форматируем часы
        if hour == 0 or hour == 24:
            hour_word = "полночь"
        elif hour == 12:
            hour_word = "полдень"
        elif hour == 1 or hour == 13:
            hour_word = "час"
        elif 2 <= hour <= 4 or 14 <= hour <= 16:
            hour_word = f"{hour % 12 if hour > 12 else hour} часа"
        else:
            hour_word = f"{hour % 12 if hour > 12 else hour} часов"
        
        # Форматируем минуты
        if minute == 0:
            minute_word = "ровно"
        elif minute == 30:
            minute_word = "половина"
        elif 1 <= minute <= 4 or 21 <= minute <= 24 or 31 <= minute <= 34 or 41 <= minute <= 44:
            minute_word = f"{minute} минуты"
        else:
            minute_word = f"{minute} минут"
        
        return f"🕐 Сейчас {hour_word} {minute_word}"
    
    def extract_city(self, text):
        """Извлечь название города из запроса погоды"""
        # Города по умолчанию
        if 'москв' in text:
            return 'Москва'
        elif 'питер' in text or 'петербург' in text or 'санкт' in text:
            return 'Санкт-Петербург'
        elif 'казан' in text:
            return 'Казань'
        elif 'сочи' in text:
            return 'Сочи'
        elif 'новосибирск' in text:
            return 'Новосибирск'
        elif 'екатеринбург' in text:
            return 'Екатеринбург'
        
        # Ищем "в городе X" или "погода X"
        words = text.split()
        if 'в' in words:
            idx = words.index('в') + 1
            if idx < len(words):
                return words[idx].capitalize()
        
        return 'Москва'  # Город по умолчанию
    
    def search_wikipedia(self, query):
        """Поиск в Википедии"""
        try:
            wiki = wikipediaapi.Wikipedia('ru')
            page = wiki.page(query)
            
            if page.exists():
                summary = page.summary.split('. ')[:2]
                result = '. '.join(summary) + '.'
                return f"📚 {result}\n\n🔗 {page.fullurl}"
            else:
                return f"❌ Ничего не найдено по запросу: {query}"
        except:
            return "⚠️ Не удалось выполнить поиск в Википедии"
    
    def play_youtube(self, query):
        """Открыть видео на YouTube"""
        try:
            pywhatkit.playonyt(query)
            return f"▶️ Открываю YouTube с запросом: {query}"
        except:
            return "⚠️ Не удалось открыть YouTube"
    
    def handle_command(self, intent, query):
        """
        Обработка команды.
        Возвращает True, если продолжаем работу, False — если выход.
        """
        
        # === ПРИВЕТСТВИЕ ===
        if intent == 'greeting':
            hour = datetime.datetime.now().hour
            if 6 <= hour < 12:
                greeting = "Доброе утро!"
            elif 12 <= hour < 18:
                greeting = "Добрый день!"
            elif 18 <= hour < 23:
                greeting = "Добрый вечер!"
            else:
                greeting = "Доброй ночи!"
            
            ui.show_response(self.name, f"👋 {greeting} Чем могу помочь?")
            return True
        
        # === ПРОЩАНИЕ ===
        elif intent == 'goodbye':
            ui.show_goodbye(self.name)
            return False
        
        # === ВРЕМЯ ===
        elif intent == 'time':
            response = self.get_time()
            ui.show_response(self.name, response)
            return True
        
        # === ПОГОДА ===
        elif intent == 'weather':
            city = self.extract_city(query)
            ui.show_response(self.name, f"🔍 Узнаю погоду в городе {city}...")
            response = weather.get_weather(city)
            ui.show_response(self.name, response)
            return True
        
        # === ПОИСК ===
        elif intent == 'search':
            ui.show_response(self.name, f"🔍 Ищу информацию: {query}")
            response = self.search_wikipedia(query)
            ui.show_response(self.name, response)
            return True
        
        # === ВИДЕО ===
        elif intent == 'video':
            if query:
                response = self.play_youtube(query)
                ui.show_response(self.name, response)
            else:
                ui.show_error("Укажите название видео. Например: видео коты")
            return True
        
        # === ПОМОЩЬ ===
        elif intent == 'help':
            ui.show_help()
            return True
        
        # === ПУСТОЙ ВВОД ===
        elif intent == 'empty':
            return True
        
        # === НЕИЗВЕСТНАЯ КОМАНДА ===
        else:
            ui.show_response(
                self.name, 
                "🤔 Я не понял команду. Напишите 'помощь' для списка команд."
            )
            return True
    
    def run(self):
        """Запуск ассистента"""
        self.running = True
        
        # Показываем приветствие
        ui.show_welcome(self.name)
        
        # Главный цикл
        while self.running:
            text = ui.get_input()
            intent, query = self.analyze_command(text)
            self.running = self.handle_command(intent, query)
        
        print(f"\n👋 Ассистент {self.name} выключен")


# Запуск
if __name__ == "__main__":
    assistant = SmartAssistant(name="Дилл")
    assistant.run()
