"""
Category and subcategory validation schemas.
"""

from marshmallow import Schema, fields, validate, pre_load
from markupsafe import escape


class CategorySchema(Schema):
    """Schema for creating a new category."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Category name is required',
            'validator_failed': 'Category name must be between 1 and 100 characters'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize category name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data


class CategoryUpdateSchema(Schema):
    """Schema for updating a category."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Category name is required',
            'validator_failed': 'Category name must be between 1 and 100 characters'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize category name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data


class SubcategorySchema(Schema):
    """Schema for creating a new subcategory."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Subcategory name is required',
            'validator_failed': 'Subcategory name must be between 1 and 100 characters'
        }
    )
    category_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'Category ID is required',
            'invalid': 'Category ID must be a valid integer',
            'validator_failed': 'Category ID must be greater than 0'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize subcategory name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data


class SubcategoryUpdateSchema(Schema):
    """Schema for updating a subcategory."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Subcategory name is required',
            'validator_failed': 'Subcategory name must be between 1 and 100 characters'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize subcategory name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data

