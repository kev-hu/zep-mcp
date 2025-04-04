@echo off
REM Script to run the Zep Cloud MCP Server on Windows

REM Navigate to the repository root directory
cd /d "%~dp0\.."

REM Find Python path
FOR /F "tokens=*" %%g IN ('where python') do (SET PYTHON_PATH=%%g)

IF "%PYTHON_PATH%"=="" (
    echo Error: Python is not installed or not in PATH. Please install Python to run this server.
    exit /b 1
)

echo Using Python at: %PYTHON_PATH%

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Creating from template...
    if exist config\.env.example (
        copy config\.env.example .env
        echo Created .env file from template. Please edit it to add your Zep API Key.
        echo You can run this script again after setting your API key.
        exit /b 1
    ) else (
        echo Error: .env.example template not found. Please create a .env file manually.
        echo It should contain: ZEP_API_KEY=your_api_key_here
        exit /b 1
    )
)

REM Install dependencies
echo Checking dependencies...
"%PYTHON_PATH%" -m pip install -r config\requirements.txt

REM Run the server
echo Starting Zep Cloud MCP Server...
fastmcp dev core\zep_cloud_server.py 