
:: Check for Python Installation
python --version 2>NUL
if errorlevel 1 goto errorNoPython

:: Python is Installed
CD ozanbot
if exist .env (pip install -r requirements.txt) else (python -m venv .env & call .env/Scripts/activate & pip install -r requirements.txt)

set env=python.exe
::cd ozanbot
call .env/Scripts/activate
echo Activated Enviroment
python ozanbot.py
echo Started bot.

PAUSE
EXIT




:: Python is NOT installed
:errorNoPython
echo.
echo Error^: Please install Python from https://www.python.org/downloads/release/python-390/
PAUSE
EXIT



