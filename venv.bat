@echo off
REM Virtual environment activation script for Windows
REM Usage: venv.bat

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated!
    echo.
    echo To deactivate, run: deactivate
) else (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
)
