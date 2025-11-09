# Security Documentation

## Overview
This document outlines the security measures implemented in InstantViz to protect user data and prevent common vulnerabilities.

## Authentication & Authorization

### Password Security

**Password Requirements (Enforced at API level):**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\/`~)

**Password Storage:**
- Passwords are hashed using **bcrypt** with auto-generated salts
- Plaintext passwords are NEVER stored in the database
- Password hashes are one-way and cannot be reversed
- Implementation: `backend/services/auth.py:15-23`

### JWT Token Security

**Token Configuration:**
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: 86-character cryptographically secure random token
- Expiration: 60 minutes (configurable)
- Token includes: user ID (sub), issued at (iat), expiration (exp)

**Token Generation:**
```python
# Secure JWT secret (infra/.env)
JWT_SECRET=xmWnH0bu1JmlHof1SqKfmGatVVCGZjmiNEcKnGC4l044A3hQQZIbTId4YMEJt6ua1cidVxP3YAJoPOUqIIApIg
```

**Token Validation:**
- All protected endpoints require Bearer token in Authorization header
- Tokens are verified on every request
- Expired tokens are automatically rejected
- Invalid tokens return 401 Unauthorized
- Implementation: `backend/utils/auth_deps.py:13-27`

### Rate Limiting

**Authentication Endpoints:**
- **Signup**: 5 attempts per minute per IP
- **Login**: 10 attempts per minute per IP
- Prevents brute force attacks
- Returns 429 Too Many Requests when limit exceeded

**Implementation:**
```python
@router.post("/signup")
@limiter.limit("5/minute")
def signup(request: Request, ...):
    ...

@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, ...):
    ...
```

## Database Security

### SQL Injection Prevention

**Protection Measures:**
- All database queries use **SQLAlchemy ORM**
- Parameterized queries prevent SQL injection
- No raw SQL execution with user input
- Input validation via Pydantic models

**Example Safe Query:**
```python
# SAFE: SQLAlchemy parameterizes automatically
user = db.query(User).filter(User.email == user_email).first()

# UNSAFE (NOT USED): Never do this!
# db.execute(f"SELECT * FROM users WHERE email = '{user_email}'")
```

### Database Credentials

**Production Credentials:**
- Strong randomly generated passwords (43-character secure tokens)
- Credentials stored in `.env` file (NOT committed to Git)
- Database exposed only to internal Docker network (not externally accessible)

```bash
POSTGRES_PASSWORD=mRQVnJuF44C0dtO-XjVW7yZVvU2OTdQAZ7rk4KJrN4g
```

## API Security

### Input Validation

**Pydantic Validation:**
- All request bodies validated via Pydantic models
- Email format validation using `EmailStr`
- Field length constraints enforced
- Type checking prevents injection attacks

**Example:**
```python
class UserCreate(BaseModel):
    email: EmailStr  # Validates RFC 5322 email format
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)  # + complexity validation
```

### Security Headers

**HTTP Security Headers (Applied to all responses):**

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | DENY | Prevents clickjacking attacks |
| `X-Content-Type-Options` | nosniff | Prevents MIME type sniffing |
| `X-XSS-Protection` | 1; mode=block | Enables browser XSS filter |
| `Content-Security-Policy` | default-src 'self'... | Prevents XSS and injection attacks |

**HTTPS Enforcement (Production):**
- Uncomment `Strict-Transport-Security` header in production
- Enforces HTTPS connections for 1 year
- Implementation: `backend/main.py:43-57`

### CORS Configuration

**Allowed Origins:**
- Explicitly configured via `CORS_ORIGINS` environment variable
- Default: `http://localhost:3000,http://localhost:8082`
- Credentials allowed only for whitelisted origins
- Prevents unauthorized cross-origin requests

```python
CORS_ORIGINS=http://localhost:3000,http://localhost:8082
```

## Sensitive Data Handling

### Environment Variables

**Never Commit Secrets:**
- `.env` file is in `.gitignore`
- All sensitive credentials in environment variables
- Separate dev/staging/production configurations

**Critical Secrets:**
- `JWT_SECRET` - JWT signing key
- `POSTGRES_PASSWORD` - Database password
- `OPENAI_API_KEY` - OpenAI API key
- `STRIPE_SECRET_KEY` - Stripe payment key
- `STRIPE_WEBHOOK_SECRET` - Webhook verification key

### API Responses

**Password Protection:**
- Passwords NEVER returned in API responses
- UserOut model explicitly excludes `password_hash` field
- Token responses only include access_token

```python
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    # password_hash is NOT included
```

## Vulnerability Prevention

### OWASP Top 10 Coverage

| Vulnerability | Status | Mitigation |
|---------------|--------|------------|
| **A01: Broken Access Control** | ✅ Protected | JWT authentication on all protected routes |
| **A02: Cryptographic Failures** | ✅ Protected | Bcrypt hashing, secure JWT secret |
| **A03: Injection** | ✅ Protected | SQLAlchemy ORM, Pydantic validation |
| **A04: Insecure Design** | ✅ Protected | Rate limiting, password complexity |
| **A05: Security Misconfiguration** | ✅ Protected | Security headers, explicit CORS |
| **A06: Vulnerable Components** | ⚠️ Monitor | Keep dependencies updated (Dependabot) |
| **A07: Auth/AuthZ Failures** | ✅ Protected | Strong passwords, JWT expiration |
| **A08: Software/Data Integrity** | ✅ Protected | No client-side validation bypass |
| **A09: Logging/Monitoring** | ⚠️ Partial | Rate limit logging (TODO: audit logs) |
| **A10: Server-Side Request Forgery** | ✅ Protected | No user-controlled URLs |

### Common Attack Mitigations

**Brute Force Attacks:**
- ✅ Rate limiting on auth endpoints
- ✅ Strong password requirements
- ✅ Account lockout (via rate limits)

**Session Hijacking:**
- ✅ JWT tokens expire after 60 minutes
- ✅ Tokens signed with secure secret
- ✅ Bearer token scheme

**Cross-Site Scripting (XSS):**
- ✅ Content-Security-Policy header
- ✅ X-XSS-Protection header
- ✅ Input sanitization via Pydantic

**Cross-Site Request Forgery (CSRF):**
- ✅ JWT tokens (not cookies)
- ✅ Explicit CORS configuration
- ✅ Same-site origin checks

**Clickjacking:**
- ✅ X-Frame-Options: DENY header

## Security Checklist

### Before Production Deployment

- [x] Generate strong JWT_SECRET (done)
- [x] Generate strong database password (done)
- [ ] Enable HTTPS/TLS on server
- [ ] Uncomment Strict-Transport-Security header
- [ ] Configure firewall rules (block direct DB access)
- [ ] Set up logging and monitoring
- [ ] Configure backup encryption
- [ ] Review all CORS_ORIGINS entries
- [ ] Rotate Stripe webhook secret
- [ ] Set up automated security scans
- [ ] Enable 2FA for admin accounts
- [ ] Configure DDoS protection (Cloudflare/AWS Shield)
- [ ] Set up intrusion detection system
- [ ] Regular dependency updates (Dependabot)

### Regular Security Maintenance

**Weekly:**
- Review failed login attempts
- Check rate limit violations
- Monitor unusual API activity

**Monthly:**
- Update dependencies (`pip list --outdated`)
- Review and rotate API keys
- Audit user permissions
- Check for CVEs in dependencies

**Quarterly:**
- Full security audit
- Penetration testing
- Review access logs
- Update security policies

## Incident Response

### If Credentials Are Compromised

**JWT_SECRET Compromised:**
1. Generate new secret: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
2. Update `.env` file
3. Restart backend service
4. All existing tokens invalidated (users must re-login)

**Database Password Compromised:**
1. Generate new password
2. Update both `.env` and PostgreSQL
3. Restart database and backend services

**Stripe Keys Compromised:**
1. Roll keys in Stripe Dashboard
2. Update `.env` file
3. Restart backend service

### Reporting Security Vulnerabilities

For security issues, please contact: security@instantviz.com (TODO: Set up dedicated email)

**Do NOT:**
- Create public GitHub issues for vulnerabilities
- Share exploit details publicly before patching

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Stripe Security](https://stripe.com/docs/security/guide)

## Compliance

**GDPR Considerations:**
- User data stored encrypted at rest (PostgreSQL)
- Users can request data deletion
- Password reset functionality
- Clear privacy policy needed (TODO)

**PCI DSS:**
- Payment processing handled by Stripe (PCI compliant)
- No credit card data stored in application
- Stripe webhook verification enforced

---

**Last Updated:** 2025-01-XX
**Security Review Date:** TODO
**Next Review Due:** TODO
