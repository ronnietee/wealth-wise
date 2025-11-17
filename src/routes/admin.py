"""
Admin portal routes with separate credential authentication.
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime, timedelta
from ..extensions import csrf

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def verify_admin_session():
    """Verify if admin session is valid."""
    if 'admin_logged_in' in session and session.get('admin_logged_in'):
        # Verify session hasn't expired (24 hours)
        if 'admin_login_time' in session:
            login_time = session['admin_login_time']
            
            # Handle both datetime objects and timestamps
            if isinstance(login_time, datetime):
                # Convert to UTC naive datetime if timezone-aware
                if login_time.tzinfo is not None:
                    login_time = login_time.replace(tzinfo=None)
                
                # Compare with UTC naive datetime
                now = datetime.utcnow()
                if (now - login_time).total_seconds() > 86400:
                    session.pop('admin_logged_in', None)
                    session.pop('admin_login_time', None)
                    return False
            elif isinstance(login_time, (int, float)):
                # Stored as timestamp
                elapsed = (datetime.utcnow().timestamp() - login_time)
                if elapsed > 86400:
                    session.pop('admin_logged_in', None)
                    session.pop('admin_login_time', None)
                    return False
        return True
    return False


def generate_admin_token():
    """Generate JWT token for admin access."""
    payload = {
        'admin': True,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_admin_token(token):
    """Verify admin JWT token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('admin') == True
    except:
        return False


@admin_bp.route('/')
def admin_index():
    """Admin portal login page."""
    if verify_admin_session():
        return render_template('admin/dashboard.html')
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
@csrf.exempt
def admin_login():
    """Admin login endpoint using environment credentials."""
    # Handle JSON parsing with better error handling
    try:
        # Log request details for debugging
        current_app.logger.debug(f'Admin login request - Content-Type: {request.content_type}, Method: {request.method}')
        
        # Try to get JSON data
        data = request.get_json(silent=True)
        
        if data is None:
            # If silent=True returned None, try to get raw data
            current_app.logger.warning('Admin login: get_json returned None, checking raw data')
            if request.data:
                try:
                    import json
                    data = json.loads(request.data.decode('utf-8'))
                except Exception as e:
                    current_app.logger.error(f'Admin login: Failed to parse JSON from raw data: {str(e)}')
                    return jsonify({'message': 'Invalid JSON in request body'}), 400
            else:
                data = {}
    except Exception as e:
        current_app.logger.error(f'Error parsing JSON in admin login: {str(e)}')
        return jsonify({'message': 'Invalid request format. Expected JSON.'}), 400
    
    username = data.get('username', '').strip() if data else ''
    password = data.get('password', '') if data else ''
    
    current_app.logger.debug(f'Admin login attempt - Username: {username}, Password provided: {bool(password)}')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    # Get admin credentials from config
    admin_username = current_app.config.get('ADMIN_USERNAME', 'admin')
    admin_password_hash = current_app.config.get('ADMIN_PASSWORD_HASH', '')
    admin_password_plain = current_app.config.get('ADMIN_PASSWORD', '')  # Fallback for migration
    
    # Check if admin password is configured
    if not admin_password_hash and not admin_password_plain:
        current_app.logger.error('ADMIN_PASSWORD_HASH or ADMIN_PASSWORD not configured in environment variables')
        return jsonify({'message': 'Admin access not configured'}), 500
    
    # Verify credentials (prefer hashed, fallback to plain for migration)
    password_valid = False
    if admin_password_hash:
        # Use hashed password (secure)
        password_valid = check_password_hash(admin_password_hash, password)
    elif admin_password_plain:
        # Fallback to plain text (for migration - should be removed)
        password_valid = (password == admin_password_plain)
        current_app.logger.warning('Using plain text admin password - migrate to ADMIN_PASSWORD_HASH')
    
    if username == admin_username and password_valid:
        # Set admin session (store timestamp to avoid timezone issues)
        session['admin_logged_in'] = True
        session['admin_login_time'] = datetime.utcnow().timestamp()  # Store as timestamp
        session['admin_username'] = username
        
        # Generate admin token
        token = generate_admin_token()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'username': username,
                'role': 'admin'
            }
        }), 200
    else:
        # Log failed admin login attempt for security monitoring
        current_app.logger.warning(
            f"Failed admin login attempt - Username: {username}, "
            f"IP: {request.remote_addr}, User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        return jsonify({'message': 'Invalid credentials'}), 401


@admin_bp.route('/logout', methods=['POST'])
@csrf.exempt
def admin_logout():
    """Admin logout endpoint."""
    session.pop('admin_logged_in', None)
    session.pop('admin_login_time', None)
    session.pop('admin_username', None)
    return jsonify({'message': 'Logout successful'}), 200


@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard page."""
    if not verify_admin_session():
        return render_template('admin/login.html')
    return render_template('admin/dashboard.html')


@admin_bp.route('/users', methods=['GET'])
def admin_users():
    """Admin users management page."""
    if not verify_admin_session():
        return render_template('admin/login.html')
    return render_template('admin/users.html')


@admin_bp.route('/subscriptions', methods=['GET'])
def admin_subscriptions_page():
    """Admin subscriptions management page."""
    if not verify_admin_session():
        return render_template('admin/login.html')
    return render_template('admin/subscriptions.html')


@admin_bp.route('/payments', methods=['GET'])
def admin_payments_page():
    """Admin payments management page."""
    if not verify_admin_session():
        return render_template('admin/login.html')
    return render_template('admin/payments.html')

