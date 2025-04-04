@echo off
REM Script to check for security issues before committing on Windows

echo [92m Checking repository for security issues...[0m

REM Navigate to the repository root
cd /d "%~dp0\.."

REM Check if .gitignore exists
if not exist .gitignore (
    echo [91m ERROR: .gitignore file does not exist![0m
    echo     Please create a .gitignore file first before adding any code.
    exit /b 1
) else (
    echo [92m .gitignore file exists[0m
)

REM Check if .env file exists with real API key
if exist .env (
    findstr /C:"ZEP_API_KEY=z_" .env >nul
    if not errorlevel 1 (
        echo [93m WARNING: .env file appears to contain a real API key[0m
        echo     This is fine for local development but should never be committed.
        echo     Verify that .env is in your .gitignore file.
    ) else (
        echo [92m .env file exists but doesn't seem to contain a real API key[0m
        echo     Remember to add your actual API key to this file.
    )
) else (
    echo [93m WARNING: No .env file found[0m
    echo     Please create a .env file from .env.example and add your API key.
)

REM Check if claude_desktop_config.json is properly configured
if exist claude_desktop_config.json (
    findstr /C:"ZEP_API_KEY" claude_desktop_config.json >nul
    if not errorlevel 1 (
        echo [91m ERROR: claude_desktop_config.json contains API key references[0m
        echo     Please remove API key references from claude_desktop_config.json.
        echo     API keys should only be stored in .env file.
    ) else (
        echo [92m claude_desktop_config.json exists and doesn't contain API keys[0m
    )
)

REM Check for Git status
where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    if exist .git (
        echo [92m Git is initialized in this repository[0m
        echo     Remember to run 'git status --ignored' before your first commit
        echo     to verify sensitive files are being ignored.
    ) else (
        echo [93m WARNING: Git is not initialized in this directory[0m
        echo     Initialize Git with 'git init' before adding any files.
    )
) else (
    echo [93m WARNING: Git is not installed or not in your PATH[0m
    echo     Install Git to use version control with this repository.
)

echo.
echo [92m Security check completed![0m
echo Remember: Never commit API keys or sensitive information to version control.
echo If this is your first time setting up the repository, make sure to:
echo 1. Commit .gitignore FIRST before any other files
echo 2. Make sure your .env file and other sensitive files are being ignored
echo 3. Follow the security guidelines in SECURITY.md
echo. 