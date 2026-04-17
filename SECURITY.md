# Security Policy

## Supported versions

Only the latest minor release is expected to receive security fixes.

## Reporting a vulnerability

Please report security issues privately before disclosing them publicly.

- Include a description of the issue.
- Include affected configuration details if possible.
- Include any reproduction steps you can safely share.

## Operational guidance

- Store upstream API keys in environment variables or a secrets manager.
- Never store API keys in committed source code, request payload templates, or plaintext files tracked by git.
- Do not commit credentials or provider tokens into the repository.
- Review provider base URLs before enabling custom endpoints.
- Rotate credentials immediately if they are ever pasted in chat, logs, screenshots, or shared terminals.
