"""Main Flask application for anonymous forum."""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, g
import time
from dotenv import load_dotenv
from app.models import db, Comment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach

try:
    # Optional; only used outside tests
    from flask_seasurf import SeaSurf  # type: ignore
except Exception:  # pragma: no cover
    SeaSurf = None  # type: ignore

# Load environment variables
load_dotenv()


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://forumuser:forumpass@localhost:5432/forumdb'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024  # 64 KiB

    # Fail fast on weak secret in non-test environments
    if not app.config.get('TESTING') and app.config['SECRET_KEY'] in ('dev-secret-key', '', None):
        raise RuntimeError('SECURITY: SECRET_KEY must be set to a strong non-default value')
    
    # Initialize database
    db.init_app(app)

    # Rate limiting (safe defaults) with storage backend (Redis in compose)
    storage_uri = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"], storage_uri=storage_uri)

    # CSRF protection only outside tests
    if not app.config.get('TESTING') and SeaSurf is not None:
        SeaSurf(app)
    
    # Routes
    @app.route('/')
    def index():
        """Main page showing all comments."""
        comments = Comment.query.order_by(Comment.created_at.asc()).all()
        return render_template('index.html', comments=comments)

    @app.route('/robots.txt')
    def robots_txt():
        return ("User-agent: *\nDisallow:\n", 200, {'Content-Type': 'text/plain; charset=utf-8'})

    @app.route('/favicon.ico')
    def favicon():
        # Avoid 404 noise; serve empty icon
        return ("", 204)
    
    @app.route('/api/comments', methods=['GET'])
    @limiter.limit("300 per minute")
    def get_comments():
        """API endpoint to get all comments."""
        comments = Comment.query.order_by(Comment.created_at.asc()).all()
        return jsonify([comment.to_dict() for comment in comments])
    
    @app.route('/api/comments', methods=['POST'])
    @limiter.limit("60 per minute")
    def post_comment():
        """API endpoint to post a new comment."""
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        content = data['content'].strip()
        
        if not content:
            return jsonify({'error': 'Content cannot be empty'}), 400
        
        if len(content) > 5000:
            return jsonify({'error': 'Content too long (max 5000 characters)'}), 400

        # Sanitize HTML: strip all tags; future-safe if rich text is enabled
        sanitized = bleach.clean(content, tags=[], attributes={}, strip=True)

        new_comment = Comment(content=sanitized)
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify(new_comment.to_dict()), 201
    
    @app.route('/post', methods=['POST'])
    @limiter.limit("60 per minute")
    def post_comment_form():
        """Form endpoint to post a new comment."""
        content = request.form.get('content', '').strip()
        
        if content:
            sanitized = bleach.clean(content, tags=[], attributes={}, strip=True)
            new_comment = Comment(content=sanitized)
            db.session.add(new_comment)
            db.session.commit()
        
        return redirect(url_for('index'))
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        try:
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    @app.after_request
    def add_security_headers(resp):
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'DENY'
        resp.headers['Referrer-Policy'] = 'same-origin'
        resp.headers['Permissions-Policy'] = "geolocation=(), microphone=(), camera=(), payment=()"
        resp.headers['Cache-Control'] = 'no-store'
        # CSP tuned for inline CSS/JS used in the template
        resp.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "object-src 'none'"
        )
        return resp

    @app.before_request
    def start_timer():
        g._start_time = time.time()

    @app.after_request
    def log_request(resp):
        try:
            duration_ms = int((time.time() - getattr(g, "_start_time", time.time())) * 1000)
            log_payload = {
                "method": request.method,
                "path": request.path,
                "status": resp.status_code,
                "duration_ms": duration_ms,
                "remote_ip": request.headers.get("X-Forwarded-For", request.remote_addr),
                "user_agent": request.headers.get("User-Agent", ""),
            }
            # Basic stdout logging in JSON-like format
            print(log_payload, flush=True)
        except Exception:
            pass
        return resp

    # Error handlers (HTML for pages, JSON for API)
    def _error_response(status_code: int, message: str):
        if request.path.startswith('/api/'):
            return jsonify({'error': message, 'status': status_code}), status_code
        # Simple HTML fallback
        return (
            f"<html><head><title>{status_code}</title></head>"
            f"<body><h1>{status_code}</h1><p>{message}</p></body></html>",
            status_code,
            {'Content-Type': 'text/html; charset=utf-8'},
        )

    @app.errorhandler(400)
    def bad_request(_e):
        return _error_response(400, 'Bad Request')

    @app.errorhandler(403)
    def forbidden(_e):
        # Security event: possible CSRF or forbidden access
        try:
            print({"event": "csrf_or_forbidden", "path": request.path, "ip": request.headers.get("X-Forwarded-For", request.remote_addr)}, flush=True)
        except Exception:
            pass
        return _error_response(403, 'Forbidden')

    @app.errorhandler(404)
    def not_found(_e):
        return _error_response(404, 'Not Found')

    @app.errorhandler(429)
    def too_many(_e):
        # Security event: rate limit exceeded
        try:
            print({"event": "rate_limit_exceeded", "path": request.path, "ip": request.headers.get("X-Forwarded-For", request.remote_addr)}, flush=True)
        except Exception:
            pass
        return _error_response(429, 'Too Many Requests')

    @app.errorhandler(500)
    def server_error(_e):
        return _error_response(500, 'Internal Server Error')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=False)
