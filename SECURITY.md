# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Mirador, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please use one of these methods:

1. **GitHub Security Advisories** (preferred): Use the "Report a vulnerability" button on the [Security tab](https://github.com/guitargnarr/mirador/security/advisories/new)
2. **Email**: Contact the maintainer directly at matthewdscott7@gmail.com with subject line `[SECURITY] Mirador vulnerability report`

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Fix timeline**: Depends on severity, targeting 30 days for critical issues

## Security Measures

Mirador implements several layers of protection:

- **245+ .gitignore patterns** preventing accidental exposure of sensitive data
- **Pre-commit hooks** scanning for credentials and personal identifiers
- **Secret scanning** enabled via GitHub
- **No external API dependencies** - all models run locally via Ollama
- **Privacy-first architecture** - no data leaves the local machine

## Best Practices for Contributors

- Never hardcode secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Run `git diff --cached` before committing to review staged changes
- Test pre-commit hooks regularly
- Report any suspicious patterns in pull requests
