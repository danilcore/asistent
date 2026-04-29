# asist.py

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pywhatkit
import wikipediaapi
import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения (для API ключей)
load_dotenv()

class SmartAssistant:
    def __init__(self, name="Assistant"):
        """
        Инициализация ассистента
        """
        self.name = name
        self.recognizer = sr.Recognizer()
        
        # Настройка голосового движка
        self.engine = pyttsx3.init()
        
        # Настройка голоса (русский)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
            
        # Настройка скорости речи
        self.engine.setProperty('rate', 100)
        
        # Словарь команд
        self.commands = {
            'приветствие': ['привет', 'здравствуй', 'добрый день'],
            'пока': ['пока', 'до свидания', 'выключись'],
            'время': ['время', 'который час', 'сколько времени'],
            'погода': ['погода', 'какая погода', 'температура'],
            'поиск': ['найди', 'поищи', 'что такое'],
            'видео': ['включи видео', 'найди видео', 'покажи видео']
        }
        
        print(f'{self.name} готов к работе')
    
    # Голосовой вывод (Text-to-Speech)
    def speak(self, text):
        """Озвучивание текста"""
        print(f"{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Прослушивание микрофона и распознания речи"""
        with sr.Microphone() as source:
            print("Слушаю...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                print(f"Вы: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                return ""
            
            except sr.UnknownValueError:
                self.speak("Извините, не расслышал. Повторите пожалуйста")
                return ""
            
            except sr.RequestError:
                self.speak("Проблемы с интернетом")
                return ""
    
    # Анализ намерений (NLP)
    def analyze_command(self, text):
        """
        Анализ команды и определение намерения
        """
        if not text:
            return None, None
        
        # Проверка на приветствие
        for phrase in self.commands['приветствие']:
            if phrase in text:
                return 'greeting', text
        
        # Проверка на прощание
        for phrase in self.commands['пока']:
            if phrase in text:
                return 'goodbye', text
        
        # Проверка на запрос времени
        for phrase in self.commands['время']:
            if phrase in text:
                return 'time', text
        
        # Проверка на запрос погоды
        for phrase in self.commands['погода']:
            if phrase in text:
                return 'weather', text
        
        # Проверка на поиск видео
        for phrase in self.commands['видео']:
            if phrase in text:
                return 'video', text
        
        # Проверка на поиск в интернете
        for phrase in self.commands['поиск']:
            if phrase in text:
                # Извлекаем поисковый запрос
                query = text.split(phrase)[-1].strip()
                return 'search', query
        
        return 'unknown', text
    
    # Модули функциональности
    def get_time(self):
        """
        Получение текущего времени
        """
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
        # Красивое форматирование времени
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
        
        if minute == 0:
            minute_word = "ровно"
        elif minute == 30:
            minute_word = "половина"
        else:
            minute_word = f"{minute} минут"
        
        return f"Сейчас {hour_word} {minute_word}"
    
    def get_weather(self, city="Москва"):
        """
        Получение погоды (нужен API ключ OpenWeatherMap)
        Бесплатный ключ: https://openweathermap.org/api
        """
        api_key = os.getenv('WEATHER_API_KEY', '')
        
        if not api_key:
            return "Для получения погоды нужен API ключ OpenWeatherMap"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
            response = requests.get(url)
            data = response.json()
            
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            feels_like = data['main']['feels_like']
            
            return f"В городе {city} сейчас {description}, температура {temp} градусов, ощущается как {feels_like}"
        
        except:
            return "Не удалось получить погоду"
    
    def search_wikipedia(self, query):
        """
        Поиск в Википедии
        """
        try:
            wiki = wikipediaapi.Wikipedia('ru')
            page = wiki.page(query)
            
            if page.exists():
                # Берём первые 2 предложения
                summary = page.summary.split('. ')[:2]
                return '. '.join(summary) + '.'
            else:
                return f"Ничего не найдено по запросу: {query}"
        except:
            return "Не удалось выполнить поиск в Википедии"
    
    def play_youtube(self, query):
        """
        Воспроизведение видео на YouTube
        """
        try:
            self.speak(f"Ищу видео: {query}")
            pywhatkit.playonyt(query)
            return f"Включаю видео по запросу: {query}"
        except:
            return "Не удалось найти видео"
    
    def web_search(self, query):
        """
        Поиск в интернете
        """
        try:
            self.speak(f"Ищу в интернете: {query}")
            pywhatkit.search(query)
            return f"Вот что нашлось по запросу: {query}"
        except:
            return "Не удалось выполнить поиск"

    # Основной цикл работы
    def handle_command(self, intent, query):
        """
        Обработка распознанной команды
        """
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
            
            self.speak(f"{greeting} Чем могу помочь?")
        
        elif intent == 'goodbye':
            self.speak("До свидания! Хорошего дня!")
            return False
        
        elif intent == 'time':
            time_response = self.get_time()
            self.speak(time_response)
        
        elif intent == 'weather':
            # Извлекаем город из запроса
            words = query.split()
            city = "Москва"  # По умолчанию
            
            # Простая проверка на город
            if 'в' in words:
                city_index = words.index('в')
                if city_index + 1 < len(words):
                    city = words[city_index + 1]
            
            weather_response = self.get_weather(city)
            self.speak(weather_response)
        
        elif intent == 'search':
            wiki_result = self.search_wikipedia(query)
            if "Ничего не найдено" in wiki_result:
                # Если в Википедии нет, ищем в интернете
                self.web_search(query)
            else:
                self.speak(wiki_result)
        
        elif intent == 'video':
            video_query = query.replace('включи видео', '').replace('найди видео', '').replace('покажи видео', '').strip()
            response = self.play_youtube(video_query)
            self.speak(response)
        
        else:
            self.speak("Я не поняла команду. Можете повторить?")
        
        return True
    
    def run(self):
        """
        Запуск ассистента
        """
        self.speak(f"Привет! Я {self.name}. Готов помочь!")
        
        running = True
        while running:
            text = self.listen()
            if text:
                intent, query = self.analyze_command(text)
                running = self.handle_command(intent, query)
        
        print("Ассистент выключен")