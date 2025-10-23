"""
Categories API routes.
"""

from flask import Blueprint, request, jsonify
from ...auth import token_required
from ...services import CategoryService

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


@categories_bp.route('/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    """Get all categories for the current user."""
    categories = CategoryService.get_user_categories(current_user.id)
    return jsonify(categories), 200


@categories_bp.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    """Create a new category."""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'message': 'Category name is required'}), 400
    
    category = CategoryService.create_category(current_user.id, name)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'is_template': category.is_template,
        'created_at': category.created_at.isoformat()
    }), 201


@categories_bp.route('/subcategories', methods=['POST'])
@token_required
def create_subcategory(current_user):
    """Create a new subcategory."""
    data = request.get_json()
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    
    if not name or not category_id:
        return jsonify({'message': 'Subcategory name and category ID are required'}), 400
    
    subcategory = CategoryService.create_subcategory(category_id, name)
    return jsonify({
        'id': subcategory.id,
        'name': subcategory.name,
        'category_id': subcategory.category_id,
        'created_at': subcategory.created_at.isoformat()
    }), 201


@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    """Update a category."""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'message': 'Category name is required'}), 400
    
    category = CategoryService.update_category(category_id, current_user.id, name)
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    return jsonify({'message': 'Category updated successfully'}), 200


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    """Delete a category."""
    success = CategoryService.delete_category(category_id, current_user.id)
    if not success:
        return jsonify({'message': 'Category not found'}), 404
    
    return jsonify({'message': 'Category deleted successfully'}), 200


@categories_bp.route('/subcategories/<int:subcategory_id>', methods=['PUT'])
@token_required
def update_subcategory(current_user, subcategory_id):
    """Update a subcategory."""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'message': 'Subcategory name is required'}), 400
    
    subcategory = CategoryService.update_subcategory(subcategory_id, name)
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404    
    return jsonify({'message': 'Subcategory updated successfully'}), 200


@categories_bp.route('/subcategories/<int:subcategory_id>', methods=['DELETE'])
@token_required
def delete_subcategory(current_user, subcategory_id):
    """Delete a subcategory."""
    success = CategoryService.delete_subcategory(subcategory_id)
    if not success:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    return jsonify({'message': 'Subcategory deleted successfully'}), 200
