"""
Categories API routes.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ...auth import token_required, subscription_required
from ...services import CategoryService
from ...schemas import (
    CategorySchema, CategoryUpdateSchema,
    SubcategorySchema, SubcategoryUpdateSchema
)
from ...utils.validation import handle_validation_error
from ...extensions import limiter

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


@categories_bp.route('/categories', methods=['GET'])
@limiter.exempt  # Exempt GET requests from rate limiting
@token_required
@subscription_required
def get_categories(current_user):
    """Get all categories for the current user."""
    categories = CategoryService.get_user_categories(current_user.id)
    return jsonify(categories), 200


@categories_bp.route('/categories', methods=['POST'])
@token_required
@subscription_required
def create_category(current_user):
    """Create a new category."""
    schema = CategorySchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    category = CategoryService.create_category(current_user.id, validated_data['name'])
    return jsonify({
        'id': category.id,
        'name': category.name,
        'is_template': category.is_template,
        'created_at': category.created_at.isoformat()
    }), 201


@categories_bp.route('/subcategories', methods=['POST'])
@token_required
@subscription_required
def create_subcategory(current_user):
    """Create a new subcategory."""
    schema = SubcategorySchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    subcategory = CategoryService.create_subcategory(
        validated_data['category_id'],
        validated_data['name']
    )
    return jsonify({
        'id': subcategory.id,
        'name': subcategory.name,
        'category_id': subcategory.category_id,
        'created_at': subcategory.created_at.isoformat()
    }), 201


@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@token_required
@subscription_required
def update_category(current_user, category_id):
    """Update a category."""
    schema = CategoryUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    category = CategoryService.update_category(category_id, current_user.id, validated_data['name'])
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    return jsonify({'message': 'Category updated successfully'}), 200


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_category(current_user, category_id):
    """Delete a category."""
    success = CategoryService.delete_category(category_id, current_user.id)
    if not success:
        return jsonify({'message': 'Category not found'}), 404
    
    return jsonify({'message': 'Category deleted successfully'}), 200


@categories_bp.route('/subcategories/<int:subcategory_id>', methods=['PUT'])
@token_required
@subscription_required
def update_subcategory(current_user, subcategory_id):
    """Update a subcategory."""
    schema = SubcategoryUpdateSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    subcategory = CategoryService.update_subcategory(subcategory_id, validated_data['name'])
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    return jsonify({'message': 'Subcategory updated successfully'}), 200


@categories_bp.route('/subcategories/<int:subcategory_id>', methods=['DELETE'])
@token_required
@subscription_required
def delete_subcategory(current_user, subcategory_id):
    """Delete a subcategory."""
    try:
        success = CategoryService.delete_subcategory(subcategory_id)
        if not success:
            return jsonify({'message': 'Subcategory not found'}), 404
        
        return jsonify({'message': 'Subcategory deleted successfully'}), 200
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error in delete_subcategory API: {str(e)}")
        return jsonify({'message': 'Error deleting subcategory'}), 500
