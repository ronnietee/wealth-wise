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
