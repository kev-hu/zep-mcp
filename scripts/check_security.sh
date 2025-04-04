#!/bin/bash
# Script to check for security issues before committing

echo "🔒 Checking repository for security issues..."

# Navigate to the repository root
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "❌ ERROR: .gitignore file does not exist!"
    echo "    Please create a .gitignore file first before adding any code."
    exit 1
else
    echo "✅ .gitignore file exists"
fi

# Check if .env is being ignored
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env is properly configured in .gitignore"
else
    echo "❌ ERROR: .env is not configured in .gitignore!"
    echo "    Please add '.env' to your .gitignore file."
    exit 1
fi

# Check if .env file exists with real API key
if [ -f ".env" ]; then
    if grep -q "ZEP_API_KEY=z_" .env || grep -q "ZEP_API_KEY=sk-" .env || grep -q "ZEP_API_KEY=[a-zA-Z0-9_-]\{30,\}" .env; then
        echo "⚠️ WARNING: .env file appears to contain a real API key"
        echo "    This is fine for local development but should never be committed."
        echo "    Verify that .env is in your .gitignore file."
    else
        echo "✅ .env file exists but doesn't seem to contain a real API key"
        echo "    Remember to add your actual API key to this file."
    fi
else
    echo "⚠️ WARNING: No .env file found"
    echo "    Please create a .env file from .env.example and add your API key."
fi

# Check if claude_desktop_config.json is properly configured
if [ -f "claude_desktop_config.json" ]; then
    if grep -q "ZEP_API_KEY" claude_desktop_config.json; then
        echo "❌ ERROR: claude_desktop_config.json contains API key references"
        echo "    Please remove API key references from claude_desktop_config.json."
        echo "    API keys should only be stored in .env file."
    else
        echo "✅ claude_desktop_config.json exists and doesn't contain API keys"
    fi
fi

# Check for any hardcoded API keys in Python files
HARDCODED_KEYS=$(grep -r "ZEP_API_KEY\s*=\s*['\"]z_" --include="*.py" . | grep -v "os.getenv" || true)
if [ -n "$HARDCODED_KEYS" ]; then
    echo "❌ ERROR: Hardcoded API keys found in the following files:"
    echo "$HARDCODED_KEYS"
    echo "    Please remove hardcoded API keys and use environment variables instead."
    exit 1
else
    echo "✅ No hardcoded API keys found in Python files"
fi

# Check git status for any files that should be excluded
if command -v git &> /dev/null && [ -d ".git" ]; then
    IGNORED_FILES=$(git status --ignored | grep -E "\.env$|venv/|__pycache__|\.pyc$" || true)
    if [ -n "$IGNORED_FILES" ]; then
        echo "✅ Git is correctly ignoring sensitive files"
    else
        echo "⚠️ WARNING: Could not verify if Git is ignoring sensitive files"
        echo "    Make sure to run 'git status --ignored' before your first commit."
    fi
else
    echo "⚠️ WARNING: Git is not initialized in this directory"
    echo "    Initialize Git with 'git init' before adding any files."
fi

echo ""
echo "🔒 Security check completed!"
echo "Remember: Never commit API keys or sensitive information to version control."
echo "If this is your first time setting up the repository, make sure to:"
echo "1. Commit .gitignore FIRST before any other files"
echo "2. Make sure your .env file and other sensitive files are being ignored"
echo "3. Follow the security guidelines in SECURITY.md"
echo "" 