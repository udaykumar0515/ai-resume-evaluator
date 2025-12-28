@echo off
REM AI Resume Evaluator - Start Script
echo ========================================
echo  AI Resume Evaluator Pro
echo  Starting Application...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate" (
    echo [ERROR] Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

REM Start Streamlit app
echo [2/2] Launching Streamlit application...
echo.
echo ========================================
echo  Application starting on http://localhost:8501
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run main_app.py

REM Deactivate on exit
deactivate
