@echo off
REM =======================================================
REM setup.bat - One-click setup for LocalHelp on Windows
REM 
REM USAGE: Double-click this file OR run in Command Prompt:
REM   setup.bat
REM =======================================================

echo ========================================
echo   LocalHelp - Setup Script
echo ========================================
echo.

REM Step 1: Install Django
echo [1/4] Installing Django...
pip install django==4.2
echo.

REM Step 2: Apply database migrations
echo [2/4] Setting up database...
python manage.py migrate
echo.

REM Step 3: Create a superuser for Django admin
echo [3/4] Creating admin user...
echo (You will be prompted to set a username and password)
python manage.py createsuperuser
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo   To start the server, run:
echo   python manage.py runserver
echo   Then open: http://127.0.0.1:8000/
echo ========================================
pause
