# modules.py
# Вспомогательные модули для текстового ассистента

import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


class WeatherNoAPI:
    """
    Погода без API ключей.
    Просто парсим данные с открытых сайтов.
    """
    
    @staticmethod
    def get_weather(city="Москва"):
        """
        Получить погоду для указанного города.
        Пробует несколько источников.
        """
        
        # Способ 1: wttr.in (самый надёжный)
        try:
            url = f"https://wttr.in/{city}?format=%C+%t&lang=ru"
            headers = {'User-Agent': 'curl/7.64.1'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"🌤 Погода в {city}: {weather_text}"
        except:
            pass
        
        # Способ 2: Яндекс.Погода (запасной)
        try:
            from bs4 import BeautifulSoup
            
            url = f"https://yandex.ru/pogoda/{city.lower().replace(' ', '-')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                temp_elem = soup.find('span', class_='temp__value')
                if temp_elem:
                    return f"🌤 Яндекс.Погода в {city}: {temp_elem.text}°C"
        except:
            pass
        
        return "❌ Не удалось получить погоду. Проверьте название города."


class TextInterface:
    """
    Текстовый интерфейс для общения с ассистентом.
    Красивое оформление, подсказки, цветной вывод.
    """
    
    @staticmethod
    def show_welcome(name):
        """Показать приветственное сообщение"""
        console.clear()
        rprint(Panel.fit(
            f"[bold cyan]🤖 {name} готов к работе![/bold cyan]\n\n"
            "[yellow]Я понимаю текстовые команды.[/yellow]\n"
            "Спросите что-нибудь или напишите [green]'помощь'[/green] для списка команд.\n"
            "Для выхода напишите [red]'пока'[/red] или [red]'выход'[/red]",
            title="Текстовый ассистент",
            border_style="cyan"
        ))
    
    @staticmethod
    def show_help():
        """Показать список доступных команд"""
        table = Table(title="📋 Доступные команды", border_style="cyan")
        table.add_column("Команда", style="green", width=30)
        table.add_column("Описание", style="white", width=50)
        
        table.add_row("привет / здравствуй", "Поздороваться с ассистентом")
        table.add_row("время / который час", "Узнать текущее время")
        table.add_row("погода / погода в Москве", "Узнать погоду (город можно указать)")
        table.add_row("найди [запрос]", "Поиск информации в Википедии")
        table.add_row("видео [название]", "Найти видео на YouTube")
        table.add_row("помощь", "Показать эту подсказку")
        table.add_row("пока / выход", "Выключить ассистента")
        
        console.print(table)
    
    @staticmethod
    def get_input():
        """Получить текстовый ввод от пользователя"""
        return Prompt.ask("\n[bold green]💬 Вы[/bold green]").strip().lower()
    
    @staticmethod
    def show_response(assistant_name, text):
        """Показать ответ ассистента"""
        rprint(Panel(text, title=f"[bold cyan]🤖 {assistant_name}[/bold cyan]"))
    
    @staticmethod
    def show_error(text):
        """Показать сообщение об ошибке"""
        rprint(f"[red]⚠️ {text}[/red]")
    
    @staticmethod
    def show_goodbye(name):
        """Показать прощальное сообщение"""
        rprint(Panel.fit(
            f"[yellow]👋 {name} завершает работу. До встречи![/yellow]",
            border_style="yellow"
        ))