@echo off
echo Запуск портала вакансий...
echo.

REM Проверяем наличие Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден! Пожалуйста, установите Python 3.x
    pause
    exit /b 1
)

REM Запускаем Python-скрипт
python launcher.py

pause 