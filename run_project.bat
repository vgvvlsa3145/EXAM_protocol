@echo off
cd /d "%~dp0"
echo Starting Secure Online Exam System...
echo -------------------------------------
if not exist venv (
    echo Virtual environment not found! Please run setup first.
    pause
    exit
)

call venv\Scripts\activate
echo Virtual Environment Activated.
echo -------------------------------------
echo MODE: LIVE MONITORING (Real-time logs enabled)
echo Access at http://0.0.0.0:8000
echo -------------------------------------
python manage.py runserver 0.0.0.0:8000
:: Alternative (Production - No Logs): waitress-serve --listen=0.0.0.0:8000 config.wsgi:application
pause
