#!/bin/bash

echo "Запуск приложения BuildIntel..."
echo ""

# Проверка наличия виртуального окружения
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "Виртуальное окружение не найдено. Создание нового..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Установка зависимостей..."
    pip install -r requirements.txt
fi

echo ""
echo "Проверка файла .env..."
if [ ! -f ".env" ]; then
    echo "ВНИМАНИЕ: Файл .env не найден!"
    echo "Создайте файл .env с вашим OPENAI_API_KEY"
    echo "Пример:"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo "OPENAI_MODEL=gpt-4o-mini"
    echo "OPENAI_VISION_MODEL=gpt-4o-mini"
    exit 1
fi

echo ""
echo "Запуск сервера на http://localhost:8000"
echo "Для остановки нажмите Ctrl+C"
echo ""
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
