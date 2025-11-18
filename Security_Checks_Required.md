# Security Checks Required

Purpose: enumerate actionable security checks and required implementations to make the app behave like a realistic production website while remaining safe. Each item includes current state, what to implement, and how to validate. Use this as a running checklist during development and reviews.

Legend:
- Priority: P0 (critical), P1 (high), P2 (medium), P3 (nice-to-have)
- Status: [x] present, [ ] missing


## Scope and Non Goals

- This application is intentionally anonymous. No authentication or authorization will be implemented.
- Do not add login, registration, roles/permissions, MFA, JWT/OAuth, or user identity features.
- All visitors can read the forum and post comments (subject to abuse protections like CSRF and rate limits).
- Security efforts focus on transport security, input validation/sanitization, abuse prevention (rate limiting), safe defaults, and infrastructure hardening.


## 1) Transport & Perimeter Security

- [ ] P0 Enforce HTTPS and HSTS
  - Current: No TLS termination or HSTS configured.
  - Implement: Place an Nginx/Traefik reverse proxy in front; redirect HTTP→HTTPS. Configure `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.
  - Validate: Access over HTTPS; curl shows HSTS header.

- [ ] P1 Redirect HTTP to HTTPS in proxy
  - Current: Not configured.
  - Implement: 301 redirect at proxy.
  - Validate: HTTP request returns 301 to HTTPS.

- [x] P2 Non-root container user
  - Current: Dockerfile creates and uses `appuser`. See `Dockerfile` (USER appuser).
  - Validate: `id` inside container shows non-root UID.


## 2) Cookie & Session Security

- [ ] P0 Secure default cookie settings
  - Current: Not set. See `app/app.py` (Flask config) — only SECRET_KEY and DB URI are configured.
  - Implement: Set `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"` in app config.
  - Validate: Browser dev tools show these flags on session cookie.

- [ ] P0 Strong, non-default `SECRET_KEY`
  - Current: Defaults to `'dev-secret-key'` when env not set. See `app/app.py`.
  - Implement: Require env var in non-test; fail fast if default is used in production.
  - Validate: Container logs on startup confirm a non-default key; add a guard to error if default.


## 3) CSRF, CORS, and Origin Protections

- [ ] P0 CSRF protection for form and JSON
  - Current: No CSRF for `/post` form or `/api/comments` JSON POST. See `app/app.py`.
  - Implement: Add `Flask-WTF` CSRF for forms; for JSON, use double-submit-cookie or header token (e.g., `X-CSRF-Token`).
  - Validate: POST without valid token returns 403; valid token succeeds.

- [ ] P1 CORS policy
  - Current: Implicit same-origin (no CORS headers).
  - Implement: Keep default same-origin; if cross-origin access is required, explicitly allow fixed origins and methods via `flask-cors` with strict settings.
  - Validate: Browser preflight behavior; curl shows absence/presence of CORS headers as intended.


## 4) Input/Output Safety (XSS, Injection)

- [x] P1 Server-side escaping for rendered content
  - Current: Jinja auto-escaping is used; no `|safe` filters. See `app/templates/index.html`:
    - `{{ comment.content }}` is escaped.
  - Validate: Post `<script>alert(1)</script>`; page shows escaped tags, no execution.

- [ ] P1 HTML sanitization if rich text ever allowed
  - Current: Only plain text accepted; 5000-char limit. See `app/app.py` (length checks).
  - Implement: If HTML is ever supported, sanitize with `bleach` (whitelist tags/attrs) before storing/rendering.
  - Validate: Malicious tags/attrs removed; allowed subset preserved.

- [x] P0 SQL injection protection via ORM
  - Current: SQLAlchemy models/queries. See `app/models.py`, `app/app.py` queries.
  - Validate: No string-built SQL; queries use ORM methods/parameters.


## 5) Abuse & DoS Hardening

- [ ] P0 Rate limiting
  - Current: None.
  - Implement: `Flask-Limiter` with IP-based quotas (e.g., `/api/comments` 10/min/IP; `/post` similar).
  - Validate: Exceeding limit returns 429; logs record rate-limit hits.

- [ ] P1 Request size and timeouts
  - Current: No explicit size limit or server timeouts.
  - Implement: `app.config['MAX_CONTENT_LENGTH']` (e.g., 64 KiB); run under Gunicorn with sane timeouts; reverse proxy timeouts.
  - Validate: Oversized requests rejected; slowloris mitigated by timeouts at proxy/WAF.

- [ ] P1 Database constraints to mirror app validation
  - Current: `comments.content` is `TEXT` without DB length constraint. See `init-db.sql`.
  - Implement: Postgres CHECK constraint `char_length(content) <= 5000` to enforce on DB side.
  - Validate: Direct insert over 5000 chars fails with constraint violation.


## 6) Error Handling & User-Facing Behavior

- [ ] P1 Custom 4xx/5xx error pages
  - Current: Default error responses.
  - Implement: Flask error handlers for 400/403/404/429/500 with friendly pages.
  - Validate: Trigger errors and verify pages; ensure no stack traces leak.

- [x] P2 Debug disabled in production path
  - Current: `debug=False` when running main; tests set `TESTING=True`. See `app/app.py`.
  - Validate: No interactive debugger; 500s don’t leak code in prod.


## 7) Headers & Browser Protections

- [ ] P0 Security headers baseline
  - Current: None added.
  - Implement: Add headers (manually or via `Flask-Talisman`):
    - Content-Security-Policy (restrict to `'self'`)
    - X-Frame-Options: DENY
    - X-Content-Type-Options: nosniff
    - Referrer-Policy: same-origin
    - Permissions-Policy: disable unused features (camera, geolocation, etc.)
  - Validate: `curl -I` shows headers; Observatory scan shows A/A+ where feasible.

- [ ] P2 Cache-control for dynamic vs static
  - Current: Not specified.
  - Implement: `Cache-Control: no-store` for dynamic HTML; reasonable caching for static assets if added.
  - Validate: Browser network panel shows expected caching.


## 8) Secrets & Configuration Management

- [ ] P0 No default `.env` in production images
  - Current: Dockerfile copies `.env.example` to `.env` in image. See `Dockerfile` (`COPY .env.example .env`).
  - Implement: Do not copy `.env.example` into production images; rely on runtime env variables only. Keep `.env.example` as template in repo.
  - Validate: Image config excludes `.env`; compose/infra injects secrets at runtime.

- [ ] P0 Required env validation
  - Current: App loads defaults silently. See `app/app.py` `load_dotenv()` and config.
  - Implement: On startup, validate required envs (SECRET_KEY, DATABASE_URL) and error if missing/unsafe defaults in non-test env.
  - Validate: Startup fails fast with clear error when misconfigured.


## 9) Database & Data Safety

- [x] P2 Parameterized access via ORM
  - Current: SQLAlchemy used.

- [ ] P1 Least-privilege DB user
  - Current: `forumuser` created with password; privileges not narrowed per table. See `init-db.sql` and `docker-compose.yml`.
  - Implement: Grant only needed privileges (CONNECT, USAGE schema, SELECT/INSERT on `comments`). Avoid SUPERUSER/CREATEDB/CREATEROLE.
  - Validate: Attempt unauthorized operations fail.

- [ ] P2 Backups/retention plan
  - Current: Not specified.
  - Implement: Add backup strategy for Postgres volume; document retention.
  - Validate: Restore test passes.


## 10) Observability & Audit

- [ ] P1 Structured logging
  - Current: No explicit logging config.
  - Implement: JSON logs with request ID, method, path, status, latency, remote IP, user-agent. Use WSGI middleware or Flask before/after_request.
  - Validate: Logs appear structured; correlation with proxy logs works.

- [ ] P1 Security/audit events
  - Current: None.
  - Implement: Log CSRF failures, rate limit hits, DB errors (without sensitive data).
  - Validate: Events visible in logs; dashboards/alerts can be built.


## 11) Dependency, Build & Supply Chain

- [ ] P0 Fix Docker healthcheck dependency
  - Current: Dockerfile healthcheck runs `python -c "import requests; ..."` but `requests` is not in `requirements.txt`. Healthcheck may fail.
  - Implement: Add `requests` to `requirements.txt` or change healthcheck to `curl`/`wget` (install minimal client) or use `CMD-SHELL` with Python stdlib `urllib.request`.
  - Validate: `docker ps` shows healthy after app starts.

- [ ] P1 Dependency scanning
  - Current: None.
  - Implement: Add `pip-audit`/`safety` to CI; add `bandit` for SAST.
  - Validate: CI fails on critical findings.

- [ ] P2 Image hardening & updates
  - Current: `python:3.11-slim` base; apt installs `postgresql-client`.
  - Implement: Regular base image updates; consider distroless/slim; remove build tools; pin apt packages when feasible.
  - Validate: Automated rebuilds pick up CVE fixes.


## 12) Runtime & Container Hardening

- [ ] P1 Drop Linux capabilities & read-only FS
  - Current: Not configured.
  - Implement: In compose/k8s, set read-only root FS, no-new-privileges, and drop all capabilities unless needed.
  - Validate: Container cannot write to root; privilege escalations blocked.

- [ ] P2 Resource limits
  - Current: None.
  - Implement: CPU/memory limits in compose/k8s; ulimits for files/processes if needed.
  - Validate: Orchestrator enforces limits.


## 13) Realistic Website Behavior (Non-security but authenticity)

- [ ] P2 404/500/maintenance pages
  - Implement: Add branded error pages; users expect them.

- [ ] P2 Static assets & caching
  - Implement: Serve basic CSS/JS, cache with ETag/Last-Modified via proxy.

- [ ] P3 robots.txt and favicon.ico
  - Implement: Add minimal assets to mirror typical sites.

- [ ] P2 Pagination or lazy loading
  - Implement: Paginate comments for realism and performance.


## File & Code References

- App configuration and routes: `app/app.py`
- Models: `app/models.py`
- Template rendering: `app/templates/index.html`
- Docker image: `Dockerfile`
- Compose configuration: `docker-compose.yml`
- DB initialization: `init-db.sql`
- Requirements: `requirements.txt`


## Quick Start for Implementations

1) App config hardening (cookies, size limits, env validation):
```python
# in app/app.py after app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=64 * 1024,  # 64 KiB
)

# fail fast on weak SECRET_KEY in non-test envs
if not app.config.get('TESTING'):
    if app.config['SECRET_KEY'] in ('dev-secret-key', '', None):
        raise RuntimeError("SECURITY: SECRET_KEY must be set to a strong value")
```

2) Rate limiting (example):
```python
# pip install Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])
limiter.limit("10/minute")(post_comment)       # for /api/comments
limiter.limit("10/minute")(post_comment_form)  # for /post
```

3) Security headers (example minimal set):
```python
@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    # Consider CSP default-src 'self' and a nonce-based policy when JS/CSS externalized
    return resp
```

4) Docker healthcheck fix (example using urllib):
```dockerfile
# Replace requests-based healthcheck with urllib (no extra deps):
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python - <<'PY' || exit 1
import urllib.request
try:
    with urllib.request.urlopen('http://localhost:5000/health', timeout=2) as r:
        exit(0 if r.status == 200 else 1)
except Exception:
    exit(1)
PY
```


## Validation Plan (Smoke Tests)

- HTTPS redirect and HSTS visible.
- Cookies have Secure/HttpOnly/SameSite flags.
- CSRF: POSTs without token fail; with token succeed.
- Rate limiting: 11th request/min returns 429.
- Oversized request rejected (413).
- DB constraint blocks >5000 chars on direct SQL insert.
- Headers present: CSP/XFO/XCTO/Referrer/Permissions.
- Healthcheck reports healthy without dependency errors.
- Error pages render without stack traces.


---
This document should be updated as protections are implemented. Keep priorities and statuses accurate to guide releases.
