# Security Policy

## Protecting Your API Keys and Sensitive Information

This document outlines security best practices for the MCP Server for Zep Cloud project.

### API Key Protection

1. **Never commit API keys to version control**
   - The `.gitignore` file is configured to prevent `.env` files from being committed
   - Always use the `.env.example` as a template to create your own `.env` file locally

2. **Rotate API keys regularly**
   - Periodically rotate your Zep Cloud API keys, especially if you suspect they might have been compromised
   - Update your `.env` file immediately after rotating keys

3. **Limit API key permissions**
   - When possible, use API keys with the minimum necessary permissions for your use case

### Configuration Files

1. **Personal configuration**
   - Files like `claude_desktop_config.json` contain personal paths and should not be committed
   - Use the example templates provided and create your own local versions

2. **Environment variables**
   - Store all sensitive information in environment variables via the `.env` file
   - Never hardcode credentials in your application code

### Development Practices

1. **First-time setup**
   - Always ensure the `.gitignore` file is in place and committed first
   - Follow the setup instructions in the README.md for a secure configuration

2. **Before committing**
   - Review changes with `git diff` to ensure no secrets are being committed
   - Use `git status --ignored` to verify sensitive files are being ignored

3. **If you accidentally commit sensitive information**
   - Immediately rotate any exposed credentials
   - Contact repository administrators for help with cleaning the Git history
   - Consider using tools like BFG Repo-Cleaner or git-filter-repo to remove sensitive data

### Report Security Issues

If you discover any security issues with this project, please contact the maintainers directly.

## Recommended Security Tools

- **Git Hooks**: Consider using pre-commit hooks to prevent committing sensitive information
- **Secret Scanning**: Tools like GitGuardian or GitHub's secret scanning feature can help detect leaked secrets
- **Environment Management**: Tools like direnv can help manage environment variables securely

Remember: Security is everyone's responsibility. When in doubt, err on the side of caution and ask for help. 