@echo off
setlocal

cd /d "%~dp0"

echo =====================================
echo PIPELINE CREATOR - SETUP
echo =====================================
echo This script prepares the application.
echo It creates the virtual environment,
echo installs dependencies and creates DB.
echo =====================================
echo.

REM =====================================================
REM Check requirements.txt
REM =====================================================

if not exist requirements.txt (
    echo ERROR: requirements.txt not found.
    echo Make sure requirements.txt is in the project root folder.
    goto error
)

REM =====================================================
REM Python check: requires Python 3.10
REM =====================================================

echo Checking Python installation...

call :find_python

IF ERRORLEVEL 1 (
    echo Python 3.10 not found.
    echo Trying to install Python 3.10 using winget...
    echo.

    winget --version >nul 2>&1
    IF ERRORLEVEL 1 (
        echo winget not found.
        echo Please install Python 3.10 manually.
        goto error
    )

    winget install -e --id Python.Python.3.10 --scope user --accept-package-agreements --accept-source-agreements
    IF ERRORLEVEL 1 goto error

    echo.
    echo Python installation completed.
    echo Checking Python again...
    echo.

    call :find_python
    IF ERRORLEVEL 1 (
        echo Python was installed but is still not available in this terminal.
        echo Close this window, reopen Command Prompt, and run this script again.
        goto error
    )
)

echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% --version

REM =====================================================
REM Virtual environment
REM =====================================================

echo.
echo Checking virtual environment...

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,10) else 1)" >nul 2>&1

    IF ERRORLEVEL 1 (
        echo Existing virtual environment does not use Python 3.10.
        echo Deleting old virtual environment...
        rmdir /s /q venv
    ) else (
        echo Existing virtual environment is compatible.
    )
)

echo.
echo Creating virtual environment...

if not exist venv (
    %PYTHON_CMD% -m venv venv
    IF ERRORLEVEL 1 goto error
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate
IF ERRORLEVEL 1 goto error

REM =====================================================
REM Install dependencies from requirements.txt
REM =====================================================

echo.
echo Upgrading pip...
python -m pip install --upgrade pip
IF ERRORLEVEL 1 goto error

echo.
echo Installing exact Python dependencies from requirements.txt...
python -m pip install -r requirements.txt
IF ERRORLEVEL 1 goto error

echo.
echo Installed main package versions:
python -c "import sys, sqlite3, fastapi, uvicorn, streamlit, sqlalchemy, requests, pydantic; print('Python:', sys.version.split()[0]); print('FastAPI:', fastapi.__version__); print('Uvicorn:', uvicorn.__version__); print('Streamlit:', streamlit.__version__); print('SQLAlchemy:', sqlalchemy.__version__); print('Requests:', requests.__version__); print('Pydantic:', pydantic.__version__); print('SQLite:', sqlite3.sqlite_version)"
IF ERRORLEVEL 1 goto error

REM =====================================================
REM Reset database
REM =====================================================

echo.
echo Preparing database...

if exist PIPELINE_CREATOR_DB.db (
    echo Existing database found.
    echo Deleting database...
    del PIPELINE_CREATOR_DB.db
) else (
    echo No existing database found.
)

REM =====================================================
REM Create database structure
REM =====================================================

echo.
echo Creating database structure...
python -m DB.CreaDB
IF ERRORLEVEL 1 goto error

REM =====================================================
REM Populate database
REM =====================================================

echo.
set /p choice=Do you want to populate the database with initial data? (Y/N): 

if /I "%choice%"=="Y" (
    echo Populating database...
    python -m DB.ValInizialeDB
    IF ERRORLEVEL 1 goto error
    echo Database successfully populated.
) else if /I "%choice%"=="N" (
    echo Database left empty.
) else (
    echo Invalid choice - database left empty.
)

echo.
echo =====================================
echo SETUP COMPLETED SUCCESSFULLY
echo =====================================
echo.

pause
exit /b 0


REM =====================================================
REM Function: find compatible Python 3.10
REM =====================================================

:find_python
set PYTHON_CMD=

py -3.10 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,10) else 1)" >nul 2>&1
IF NOT ERRORLEVEL 1 (
    set PYTHON_CMD=py -3.10
    exit /b 0
)

python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,10) else 1)" >nul 2>&1
IF NOT ERRORLEVEL 1 (
    set PYTHON_CMD=python
    exit /b 0
)

exit /b 1


:error
echo.
echo =====================================
echo ERROR DURING SETUP
echo =====================================
echo.
pause
exit /b 1
