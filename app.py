import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)
urls_to_ping = os.environ.get('URLS_TO_PING', '').split(',')
urls_to_ping = [url.strip() for url in urls_to_ping if url.strip()]
ping_interval = int(os.environ.get('PING_INTERVAL', 30))

def ping_urls():
    while True:
        for url in urls_to_ping:
            try:
                response = requests.get(url, timeout=10)
                print(f"[{datetime.now()}] Пинг {url} - Статус: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[{datetime.now()}] Ошибка при пинге {url}: {e}")
        time.sleep(ping_interval)

@app.route('/')
def index():
    return jsonify({
        'status': 'active',
        'urls_to_ping': urls_to_ping,
        'ping_interval_seconds': ping_interval
    })

@app.route('/ping')
def manual_ping():
    results = []
    for url in urls_to_ping:
        try:
            response = requests.get(url, timeout=10)
            results.append({
                'url': url,
                'status': response.status_code,
                'success': True
            })
        except Exception as e:
            results.append({
                'url': url,
                'status': str(e),
                'success': False
            })
    return jsonify(results)

if __name__ == '__main__':
    if urls_to_ping:
        ping_thread = threading.Thread(target=ping_urls, daemon=True)
        ping_thread.start()
        print(f"Запущен пингер для URL: {urls_to_ping}")
        print(f"Интервал пинга: {ping_interval} секунд")
    else:
        print("ВНИМАНИЕ: Не указаны URL для пинга. Добавьте переменную окружения URLS_TO_PING")
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
