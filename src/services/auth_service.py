"""
Authentication service for user management.
"""

import jwt
import secrets
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from ..extensions import db
from ..models import User, PasswordResetToken, EmailVerification
from ..utils.email import send_verification_email, send_password_reset_email


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password."""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
    
    @staticmethod
    def generate_jwt_token(user, app_config, request=None):
        """Generate JWT token for user."""
        from flask import request as flask_request
        if request is None:
            request = flask_request
        
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1),  # Reduced from 24 hours to 1 hour
            'iat': datetime.utcnow()
        }
        
        # Optionally bind token to IP address for additional security
        if request:
            payload['ip'] = request.remote_addr
        
        return jwt.encode(payload, app_config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def create_password_reset_token(user):
        """Create password reset token for user."""
        # Delete any existing tokens for this user
        PasswordResetToken.query.filter_by(user_id=user.id, used=False).delete()
        
        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()
        
        return token
    
    @staticmethod
    def _has_verified_column():
        """Check if email_verification table has verified column."""
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('email_verification')]
            return 'verified' in columns
        except Exception:
            # If check fails, assume column doesn't exist to be safe
            return False
    
    @staticmethod
    def create_email_verification_token(user):
        """Create email verification token for user."""
        # Delete any existing tokens for this user
        # Handle case where verified column might not exist
        if AuthService._has_verified_column():
            EmailVerification.query.filter_by(user_id=user.id, verified=False).delete()
        else:
            # If verified column doesn't exist, delete all tokens for this user
            EmailVerification.query.filter_by(user_id=user.id).delete()
        
        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        verification_token = EmailVerification(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(verification_token)
        db.session.commit()
        
        return token
    
    @staticmethod
    def verify_password_reset_token(token):
        """Verify password reset token and return user if valid."""
        reset_token = PasswordResetToken.query.filter_by(
            token=token, 
            used=False
        ).first()
        
        if not reset_token or reset_token.expires_at < datetime.utcnow():
            return None
        
        return reset_token.user
    
    @staticmethod
    def verify_email_token(token):
        """Verify email verification token and return user if valid."""
        # Handle case where verified column might not exist
        if AuthService._has_verified_column():
            verification_token = EmailVerification.query.filter_by(
                token=token, 
                verified=False
            ).first()
        else:
            # If verified column doesn't exist, just check token
            verification_token = EmailVerification.query.filter_by(token=token).first()
        
        if not verification_token or verification_token.expires_at < datetime.utcnow():
            return None
        
        # Get the user by user_id
        from ..models import User
        return User.query.get(verification_token.user_id)
    
    @staticmethod
    def mark_password_reset_token_used(token):
        """Mark password reset token as used."""
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token:
            reset_token.used = True
            db.session.commit()
    
    @staticmethod
    def mark_email_verified(token):
        """Mark email as verified."""
        verification_token = EmailVerification.query.filter_by(token=token).first()
        if verification_token:
            # Only set verified if column exists
            if AuthService._has_verified_column():
                verification_token.verified = True
            # Get the user by user_id and mark email as verified
            from ..models import User
            user = User.query.get(verification_token.user_id)
            if user:
                user.email_verified = True
            db.session.commit()
