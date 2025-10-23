"""
Authentication and authorization utilities.
"""

from functools import wraps
from flask import request, jsonify, session
import jwt
from ..extensions import db
from ..models import User


def token_required(f):
    """Decorator for JWT token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # Import User here to avoid circular import issues
            from ..models import User
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"Token validation error: {e}")
            return jsonify({'message': 'Token validation failed!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


def validate_session():
    """Validate current session and clear if invalid."""
    if 'user_id' in session and 'logged_in' in session:
        user = User.query.get(session['user_id'])
        if not user:
            # User no longer exists, clear session
            session.clear()
            return False
        return True
    return False


def get_current_user():
    """Get current user from JWT token in Authorization header or from session."""
    # Try JWT token first
    token = request.headers.get('Authorization')
    if token:
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, request.app.config['SECRET_KEY'], algorithms=['HS256'])
            return User.query.filter_by(id=data['user_id']).first()
        except:
            pass
    
    # Fall back to session
    if 'user_id' in session and 'logged_in' in session:
        return User.query.get(session['user_id'])
    
    return None
