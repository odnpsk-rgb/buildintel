@echo off
echo Запуск приложения BuildIntel...
echo.

REM Проверка наличия виртуального окружения
if exist venv\Scripts\activate.bat (
    echo Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo Виртуальное окружение не найдено. Создание нового...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Установка зависимостей...
    pip install -r requirements.txt
)

echo.
echo Проверка файла .env...
if not exist .env (
    echo ВНИМАНИЕ: Файл .env не найден!
    echo Создайте файл .env с вашим OPENAI_API_KEY
    echo Пример:
    echo OPENAI_API_KEY=your_api_key_here
    echo OPENAI_MODEL=gpt-4o-mini
    echo OPENAI_VISION_MODEL=gpt-4o-mini
    pause
    exit /b 1
)

echo.
echo Запуск сервера на http://localhost:8000
echo Для остановки нажмите Ctrl+C
echo.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
