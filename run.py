# run.py - Файл для запуска

import asist as asi

if __name__ == "__main__":
    # Создаём и запускаем ассистента
    assistant = asi.SmartAssistant(name="Дилл")
    assistant.run()