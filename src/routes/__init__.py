"""
Route blueprints for the Wealth Wise application.
"""

from .main import main_bp
from .auth import auth_bp
from .api import api_bp
from .admin import admin_bp

__all__ = ['main_bp', 'auth_bp', 'api_bp', 'admin_bp']
