@echo off

echo =====================================
echo PIPELINE CREATOR - APPLICATION START
echo =====================================
echo.

REM --- Python check ---
echo Checking Python installation...
python --version
IF ERRORLEVEL 1 goto error

REM --- check virtual environment ---
echo Checking virtual environment...
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run setup_db.bat first
    pause
    exit /b
)

REM --- activate venv ---
echo Activating virtual environment...
call venv\Scripts\activate
IF ERRORLEVEL 1 goto error

REM --- start backend ---
echo Starting FastAPI backend server...
start "FastAPI Server" cmd /k python -m uvicorn main:app --reload

echo Waiting for backend initialization...
timeout /t 3 >nul

REM --- start frontend ---
echo Starting Streamlit user interface...
start "Streamlit UI" cmd /k python -m streamlit run InterfacciaUtente.py

echo.
echo =====================================
echo APPLICATION STARTED SUCCESSFULLY
echo =====================================
echo Backend API available at:
echo http://127.0.0.1:8000/docs
echo.
echo User interface available at:
echo http://localhost:8501
echo =====================================
echo.

pause
exit /b

:error
echo.
echo ERROR during application startup
pause
