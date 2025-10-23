"""
User API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required, get_current_user
from ...services import UserService, EmailService
from ...utils.currency import get_currency_symbol

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile')
@token_required
def get_user_profile(current_user):
    """Get current user profile."""
    
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'display_name': current_user.display_name,
        'currency': current_user.currency,
        'theme': current_user.theme,
        'email_verified': current_user.email_verified,
        'created_at': current_user.created_at.isoformat()
    }), 200


@user_bp.route('/settings', methods=['GET'])
@token_required
def get_user_settings(current_user):
    """Get user settings."""
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'display_name': current_user.display_name,
        'currency': current_user.currency,
        'theme': current_user.theme,
        'email_verified': current_user.email_verified
    }), 200


@user_bp.route('/settings', methods=['PUT'])
@token_required
def update_user_settings(current_user):
    """Update user settings."""
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'display_name', 'currency', 'theme']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({'message': 'No valid fields to update'}), 400
    
    UserService.update_user_settings(current_user, **update_data)
    
    return jsonify({'message': 'Settings updated successfully'}), 200


@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password."""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': 'Old and new passwords are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': 'New password must be at least 6 characters long'}), 400
    
    success, error = UserService.change_password(current_user, old_password, new_password)
    if not success:
        return jsonify({'message': error}), 400
    
    return jsonify({'message': 'Password changed successfully'}), 200


@user_bp.route('/reset-data', methods=['POST'])
@token_required
def reset_user_data(current_user):
    """Reset all user data except account."""
    success, error = UserService.reset_user_data(current_user)
    if not success:
        return jsonify({'message': error}), 500
    
    return jsonify({'message': 'Data reset successfully'}), 200


@user_bp.route('/delete-account', methods=['POST'])
@token_required
def delete_user_account(current_user):
    """Delete user account."""
    data = request.get_json()
    confirm_password = data.get('password')
    
    if not confirm_password:
        return jsonify({'message': 'Password confirmation is required'}), 400
    
    # Verify password
    from werkzeug.security import check_password_hash
    if not check_password_hash(current_user.password_hash, confirm_password):
        return jsonify({'message': 'Incorrect password'}), 400
    
    success, error = UserService.delete_user(current_user)
    if not success:
        return jsonify({'message': error}), 500
    
    return jsonify({'message': 'Account deleted successfully'}), 200


@user_bp.route('/export-data', methods=['GET'])
@token_required
def export_user_data(current_user):
    """Export user data to Excel."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import io
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "User Data Export"
        
        # Add headers
        headers = ['Data Type', 'Name', 'Amount', 'Date', 'Description', 'Category', 'Subcategory']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        row = 2
        
        # Add user info
        ws.cell(row=row, column=1, value="User Info")
        ws.cell(row=row, column=2, value=f"{current_user.first_name} {current_user.last_name}")
        ws.cell(row=row, column=3, value=current_user.email)
        row += 1
        
        # Add categories
        from ..models import Category, Subcategory
        categories = Category.query.filter_by(user_id=current_user.id).all()
        for category in categories:
            ws.cell(row=row, column=1, value="Category")
            ws.cell(row=row, column=2, value=category.name)
            row += 1
            
            for subcategory in category.subcategories:
                ws.cell(row=row, column=1, value="Subcategory")
                ws.cell(row=row, column=2, value=subcategory.name)
                ws.cell(row=row, column=6, value=category.name)
                row += 1
        
        # Add transactions
        from ..models import Transaction
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        for transaction in transactions:
            ws.cell(row=row, column=1, value="Transaction")
            ws.cell(row=row, column=2, value=transaction.description or "")
            ws.cell(row=row, column=3, value=transaction.amount)
            ws.cell(row=row, column=4, value=transaction.transaction_date.strftime('%Y-%m-%d'))
            ws.cell(row=row, column=5, value=transaction.comment or "")
            ws.cell(row=row, column=6, value=transaction.subcategory.category.name)
            ws.cell(row=row, column=7, value=transaction.subcategory.name)
            row += 1
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        from flask import send_file
        return send_file(
            output,
            as_attachment=True,
            download_name=f"steward_export_{current_user.username}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        return jsonify({'message': f'Export failed: {str(e)}'}), 500


@user_bp.route('/theme', methods=['PUT'])
@token_required
def update_user_theme(current_user):
    """Update user theme preference."""
    data = request.get_json()
    theme = data.get('theme')
    
    if theme not in ['light', 'dark']:
        return jsonify({'message': 'Invalid theme. Must be "light" or "dark"'}), 400
    
    current_user.theme = theme
    from ..extensions import db
    db.session.commit()
    
    return jsonify({'message': 'Theme updated successfully'}), 200
