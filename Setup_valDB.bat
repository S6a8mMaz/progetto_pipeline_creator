@echo off

echo =====================================
echo PIPELINE CREATOR - DATABASE SETUP
echo =====================================
echo This script prepares the database and
echo optionally loads initial example data
echo =====================================
echo.

REM --- Python check ---
echo Checking Python installation...
python --version
IF ERRORLEVEL 1 goto error

REM --- virtual environment ---
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo Activating virtual environment...
call venv\Scripts\activate
IF ERRORLEVEL 1 goto error

REM --- install dependencies ---
echo Installing required dependencies...
pip install fastapi uvicorn streamlit sqlalchemy

REM --- reset DB ---
echo.
echo Preparing database...

if exist PIPELINE_CREATOR_DB.db (
    echo Existing database found
    echo Deleting database...
    del PIPELINE_CREATOR_DB.db
) else (
    echo No existing database found
)

REM --- create DB ---
echo.
echo Creating database structure...
python -m DB.CreaDB
IF ERRORLEVEL 1 goto error

REM --- user choice ---
echo.
set /p choice=Do you want to populate the database with initial data? (Y/N): 

if /I "%choice%"=="Y" (
    echo Populating database...
    python -m DB.ValInizialeDB
    IF ERRORLEVEL 1 goto error
    echo Database successfully populated
) else if /I "%choice%"=="N" (
    echo Database left empty
) else (
    echo Invalid choice - database left empty
)

echo.
echo =====================================
echo DATABASE SETUP COMPLETED
echo =====================================
echo.

pause
exit /b

:error
echo.
echo ERROR during database setup
pause