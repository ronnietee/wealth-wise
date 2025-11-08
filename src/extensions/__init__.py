"""
Flask extensions initialization.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def init_extensions(app):
    """Initialize Flask extensions with the app."""
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    csrf.init_app(app)
    
    limiter.init_app(app)
    
    # Initialize Talisman with security headers
    # Only force HTTPS in production
    import os
    force_https = os.environ.get('FLASK_ENV') == 'production' or not app.config.get('DEBUG', False)
    Talisman(
        app,
        force_https=force_https,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' blob: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
            'script-src-elem': "'self' 'unsafe-inline' blob: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
            'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            'img-src': "'self' data: https:",
            'font-src': "'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com",
            'connect-src': "'self' https://cdn.jsdelivr.net"
        },
        frame_options='DENY',
        x_content_type_options=True,
        referrer_policy='strict-origin-when-cross-origin'
    )
