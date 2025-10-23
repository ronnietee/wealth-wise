"""
Authentication-related models for password reset and email verification.
"""

from datetime import datetime
from ..extensions import db


class PasswordResetToken(db.Model):
    """Password reset token model for secure password resets."""
    
    __tablename__ = 'password_reset_token'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:10]}...>'


class EmailVerification(db.Model):
    """Email verification token model for email verification."""
    
    __tablename__ = 'email_verification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailVerification {self.token[:10]}...>'
