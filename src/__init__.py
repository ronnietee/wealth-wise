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
    
    # Ensure all API routes are exempt from CSRF (they use JWT tokens)
    # Exempt after registration to ensure all nested blueprints are covered
    from .extensions import csrf
    from .routes.api import user_bp, categories_bp, transactions_bp, budget_bp, accounts_bp, recurring_bp, subscriptions_bp
    
    # Exempt all nested API blueprints
    csrf.exempt(api_bp)
    csrf.exempt(user_bp)
    csrf.exempt(categories_bp)
    csrf.exempt(transactions_bp)
    csrf.exempt(budget_bp)
    csrf.exempt(accounts_bp)
    csrf.exempt(recurring_bp)
    csrf.exempt(subscriptions_bp)
    
    return app
