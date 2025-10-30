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


def subscription_required(f):
    """Decorator to enforce active subscription or valid trial depending on config flags."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        from flask import current_app
        if not current_app.config.get('SUBSCRIPTIONS_ENABLED', True):
            return f(current_user, *args, **kwargs)

        # If enforcement is off, allow during trial period without blocking
        enforce = current_app.config.get('ENFORCE_PAYMENT_AFTER_TRIAL', False)

        # Evaluate user status
        status = (current_user.subscription_status or 'trial').lower()
        now = datetime.utcnow()
        trial_end = current_user.trial_end

        if status == 'active':
            return f(current_user, *args, **kwargs)

        if status == 'trial':
            if trial_end is None or now <= trial_end:
                return f(current_user, *args, **kwargs)
            # Trial expired
            if not enforce:
                return f(current_user, *args, **kwargs)
            return jsonify({'message': 'Trial expired. Subscription required.'}), 402

        # past_due or cancelled
        if not enforce:
            return f(current_user, *args, **kwargs)
        return jsonify({'message': 'Subscription required to access this feature.'}), 402

    from datetime import datetime
    from flask import jsonify
    return decorated