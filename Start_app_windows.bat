@echo off
setlocal

cd /d "%~dp0"

echo =====================================
echo PIPELINE CREATOR - APPLICATION START
echo =====================================
echo.

REM =====================================================
REM Check virtual environment
REM =====================================================

echo Checking virtual environment...

if not exist venv\Scripts\python.exe (
    echo ERROR: Virtual environment not found.
    echo Please run Setup_valDB_windows.bat first.
    echo.
    pause
    exit /b 1
)

REM =====================================================
REM Activate virtual environment
REM =====================================================

echo Activating virtual environment...
call venv\Scripts\activate

IF ERRORLEVEL 1 (
    echo ERROR: unable to activate virtual environment.
    pause
    exit /b 1
)

REM =====================================================
REM Check Python and required packages
REM =====================================================

echo.
echo Checking installed packages...

python -c "import fastapi, uvicorn, streamlit, sqlalchemy, requests, pydantic"
IF ERRORLEVEL 1 (
    echo ERROR: some required Python packages are missing.
    echo Please run Setup_valDB_windows.bat again.
    echo.
    pause
    exit /b 1
)

REM =====================================================
REM Start backend
REM =====================================================

echo.
echo Starting FastAPI backend server...

start "FastAPI Backend" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for backend initialization...
timeout /t 3 >nul

REM =====================================================
REM Start frontend
REM =====================================================

echo.
echo Starting Streamlit user interface...

start "Streamlit Frontend" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate && python -m streamlit run InterfacciaUtente.py"

echo.
echo =====================================
echo APPLICATION STARTED SUCCESSFULLY
echo =====================================
echo Backend API documentation:
echo http://127.0.0.1:8000/docs
echo.
echo User interface:
echo http://localhost:8501
echo =====================================
echo.

pause
exit /b 0
