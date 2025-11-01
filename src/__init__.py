"""
Wealth Wise application factory.
"""

from flask import Flask
from .config import config
from .extensions import init_extensions
from .routes import main_bp, auth_bp, api_bp, admin_bp


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    return app
