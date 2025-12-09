# Security Notes

- Passwords hashed with bcrypt (via PasswordManager).
- Encryption helpers use PBKDF2-HMAC for sensitive data.
- Roles stored as strings (`admin`, `coach`, `captain`, `member`).
- Sessions managed per repository call; relationships are eager-loaded to avoid detached errors.
- Audit logs capture key actions (create/update/delete where implemented).

Recommendations:
- Rotate DB credentials for production.
- Enforce SSL/TLS on MySQL in production.
- Add rate limiting or CAPTCHA to signup/login in future.
