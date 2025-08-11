@echo off
REM Zep Cloud MCP Server Wrapper Script for Windows
REM This script provides a portable way to run the Zep Cloud MCP Server on Windows

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
for %%i in ("%SCRIPT_DIR%..") do set PROJECT_DIR=%%~fi

REM Check if virtual environment exists and activate it
if exist "%PROJECT_DIR%\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_DIR%\venv\Scripts\activate.bat"
) else if exist "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    echo Activating virtual environment (.venv)...
    call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
) else (
    echo Warning: No virtual environment found. Using system Python.
)

REM Change to project directory to ensure relative imports work
cd /d "%PROJECT_DIR%"

REM Run the MCP server
python "%PROJECT_DIR%\core\zep_cloud_server.py" %*
