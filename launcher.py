import os
import sys
import webbrowser
import subprocess
import time
from threading import Thread

def open_browser():
    """Открывает браузер после небольшой задержки"""
    time.sleep(2)  # Ждем 2 секунды, чтобы сервер успел запуститься
    webbrowser.open('http://localhost:5000')

def main():
    # Определяем путь к Python-интерпретатору
    python = sys.executable
    
    # Запускаем сервер в отдельном потоке
    server_thread = Thread(target=lambda: subprocess.run([python, 'main.py']))
    server_thread.daemon = True
    server_thread.start()
    
    # Открываем браузер
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("Запуск сервера...")
    print("Открытие браузера...")
    print("\nДля остановки сервера нажмите Ctrl+C")
    
    try:
        # Держим скрипт запущенным
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        sys.exit(0)

if __name__ == '__main__':
    main() 