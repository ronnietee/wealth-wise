"""
Authentication routes.
"""

from flask import Blueprint, render_template, request, jsonify, session
from ..auth import get_current_user
from ..services import AuthService, UserService, EmailService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/reset-password')
def reset_password_page():
    """Password reset page."""
    token = request.args.get('token')
    if not token:
        return render_template('reset_password.html', error='Invalid reset link')
    
    # Verify token is valid
    user = AuthService.verify_password_reset_token(token)
    if not user:
        return render_template('reset_password.html', error='Invalid or expired reset link')
    
    return render_template('reset_password.html', token=token)


@auth_bp.route('/verify-email')
def verify_email():
    """Email verification page."""
    token = request.args.get('token')
    if not token:
        return render_template('email_verification.html', error='Invalid verification link')
    
    user = AuthService.verify_email_token(token)
    if not user:
        return render_template('email_verification.html', error='Invalid or expired verification link')
    
    # Mark email as verified
    AuthService.mark_email_verified(token)
    return render_template('email_verification.html', success=True)


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    
    # Validation
    if not all([username, email, password, first_name, last_name]):
        return jsonify({'message': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400
    
    # Create user
    user, error = UserService.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    if error:
        return jsonify({'message': error}), 400
    
    # Create email verification token
    verification_token = AuthService.create_email_verification_token(user)
    
    # Send verification email
    from flask import current_app
    EmailService.send_verification_email(user, verification_token, current_app.config)
    
    return jsonify({
        'message': 'Registration successful! Please check your email to verify your account.',
        'user_id': user.id
    }), 201


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Login user with JWT token."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Check if either email or username is provided
        if not password or (not email and not username):
            return jsonify({'message': 'Email/username and password are required'}), 400
        
        # If username is provided, find user by username
        if username and not email:
            user = UserService.get_user_by_username(username)
        else:
            # Use email for authentication
            user = AuthService.authenticate_user(email, password)
        
        # If we found user by username, verify password
        if username and not email and user:
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password_hash, password):
                user = None
        
        if not user:
            return jsonify({'message': 'Invalid email/username or password'}), 401
        
        # Check if email is verified
        if not user.email_verified:
            return jsonify({
                'message': 'Please verify your email before logging in. Check your inbox for the verification email.',
                'email_verified': False
            }), 403
        
        # Generate JWT token
        from flask import current_app
        token = AuthService.generate_jwt_token(user, current_app.config)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'display_name': user.display_name,
                'currency': user.currency,
                'theme': user.theme,
                'email_verified': user.email_verified
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def frontend_login():
    """Login route for frontend form submission with session management."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not password or (not email and not username):
        return jsonify({'message': 'Email/username and password are required'}), 400
    
    # If username is provided, find user by username
    if username and not email:
        user = UserService.get_user_by_username(username)
        if user:
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password_hash, password):
                user = None
    else:
        user = AuthService.authenticate_user(email, password)
    
    if not user:
        return jsonify({'message': 'Invalid email/username or password'}), 401
    
    # Check if email is verified
    if not user.email_verified:
        return jsonify({
            'message': 'Please verify your email before logging in. Check your inbox for the verification email.',
            'email_verified': False
        }), 403
    
    # Set session
    session['user_id'] = user.id
    session['logged_in'] = True
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': user.display_name,
            'currency': user.currency,
            'theme': user.theme,
            'email_verified': user.email_verified
        }
    }), 200


@auth_bp.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get CSRF token for frontend forms."""
    return jsonify({'csrf_token': 'dummy_token'})  # Temporary for testing


@auth_bp.route('/api/session/validate', methods=['GET'])
def validate_user_session():
    """Validate current user session and return user info."""
    user = get_current_user()
    if not user:
        return jsonify({'message': 'No valid session'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': user.display_name,
            'currency': user.currency,
            'theme': user.theme,
            'email_verified': user.email_verified
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout route to clear session."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API logout route."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200
    
    # Create password reset token
    reset_token = AuthService.create_password_reset_token(user)
    
    # Send reset email
    from flask import current_app
    EmailService.send_password_reset_email(user, reset_token, current_app.config)
    
    return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200


@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset user password."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400
    
    user = AuthService.verify_password_reset_token(token)
    if not user:
        return jsonify({'message': 'Invalid or expired reset token'}), 400
    
    # Update password
    user.set_password(new_password)
    from ..extensions import db
    db.session.commit()
    
    # Mark token as used
    AuthService.mark_password_reset_token_used(token)
    
    return jsonify({'message': 'Password reset successful'}), 200
