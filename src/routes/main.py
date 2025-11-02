"""
Main routes for static pages.
"""

from flask import Blueprint, render_template, send_file, request, jsonify
from ..auth import get_current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page."""
    return render_template('dashboard.html')


@main_bp.route('/budgets')
def budgets():
    """Budgets page."""
    return render_template('budgets.html')


@main_bp.route('/income')
def income():
    """Income page."""
    return render_template('income.html')


@main_bp.route('/breakdown')
def breakdown():
    """Breakdown page."""
    return render_template('breakdown.html')


@main_bp.route('/input')
def input_page():
    """Input page."""
    return render_template('input.html')


@main_bp.route('/transactions')
def transactions():
    """Transactions page."""
    return render_template('transactions.html')


@main_bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


@main_bp.route('/accounts')
def accounts_page():
    """Accounts page."""
    return render_template('accounts.html')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


@main_bp.route('/help')
def help():
    """Help page."""
    return render_template('help.html')


@main_bp.route('/onboarding')
def onboarding():
    """Onboarding page for new users."""
    return render_template('onboarding.html')


@main_bp.route('/favicon.ico')
def favicon():
    """Favicon."""
    return send_file('../static/images/logo.png', mimetype='image/png')


@main_bp.route('/payfast/return')
def payfast_return():
    """PayFast return URL - user redirected here after successful payment setup during onboarding."""
    # Extract query parameters if any
    payment_id = request.args.get('pf_payment_id', '')
    payment_status = request.args.get('payment_status', '').upper()
    
    # Check if user is coming from onboarding (no session yet) or settings
    from flask import redirect, url_for, flash, session
    from ...models import User
    
    # Try to identify user from session or token
    user_id = session.get('user_id') or None
    token = request.args.get('token')
    
    # If coming from onboarding, redirect to dashboard with success message
    if not user_id and not token:
        # Coming from onboarding - payment setup completed
        flash('Payment method set up successfully! Your 30-day free trial has started.', 'success')
        return redirect(url_for('main.index'))
    
    # Otherwise redirect to settings page with success message
    if payment_status == 'COMPLETE':
        flash('Payment successful! Your subscription has been activated.', 'success')
    elif payment_status == 'PENDING':
        flash('Payment is pending. Your subscription will be activated once payment is confirmed.', 'info')
    else:
        flash('Payment method set up successfully!', 'success')
    
    return redirect(url_for('main.settings'))


@main_bp.route('/payfast/cancel')
def payfast_cancel():
    """PayFast cancel URL - user redirected here if payment is cancelled."""
    from flask import redirect, url_for, flash, session
    
    # Check if user is coming from onboarding (no session yet) or settings
    user_id = session.get('user_id') or None
    
    if not user_id:
        # Coming from onboarding - allow user to continue with trial, setup payment later
        flash('You can continue with your free trial. Set up payment anytime from Settings to ensure uninterrupted service.', 'info')
        return redirect(url_for('main.index'))
    
    # Otherwise redirect to settings
    flash('Payment was cancelled. You can try again from your subscription settings.', 'warning')
    return redirect(url_for('main.settings'))