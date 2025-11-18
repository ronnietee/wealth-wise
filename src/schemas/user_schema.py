"""
User and onboarding validation schemas.
"""

from marshmallow import Schema, fields, validate, pre_load, validates, EXCLUDE
from markupsafe import escape
from ..utils.password import validate_password_strength


class ContactFormSchema(Schema):
    """Schema for contact form submission."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Name is required',
            'validator_failed': 'Name must be between 1 and 100 characters'
        }
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please provide a valid email address',
            'validator_failed': 'Email must be 255 characters or less'
        }
    )
    subject = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={
            'required': 'Subject is required',
            'validator_failed': 'Subject must be between 1 and 200 characters'
        }
    )
    message = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            'required': 'Message is required',
            'validator_failed': 'Message must be between 1 and 2000 characters'
        }
    )
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        for field in ['name', 'subject', 'message']:
            if field in data and data[field]:
                data[field] = escape(str(data[field])).strip()
        return data


class OnboardingSchema(Schema):
    """Schema for onboarding/registration."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    username = fields.Str(
        validate=validate.Length(min=3, max=50),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Username must be between 3 and 50 characters'
        }
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please provide a valid email address',
            'validator_failed': 'Email must be 255 characters or less'
        }
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=12),
        error_messages={
            'required': 'Password is required',
            'validator_failed': 'Password must be at least 12 characters long'
        }
    )
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'First name is required',
            'validator_failed': 'First name must be between 1 and 100 characters'
        }
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Last name is required',
            'validator_failed': 'Last name must be between 1 and 100 characters'
        }
    )
    country = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Country must be 100 characters or less'
        }
    )
    preferred_name = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Preferred name must be 100 characters or less'
        }
    )
    referral_source = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Referral source must be 100 characters or less'
        }
    )
    referral_details = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Referral details must be 500 characters or less'
        }
    )
    currency = fields.Str(
        validate=validate.Length(max=10),
        load_default='USD',
        error_messages={
            'validator_failed': 'Currency must be 10 characters or less'
        }
    )
    accept_terms = fields.Bool(
        required=True,
        error_messages={
            'required': 'You must accept the Terms and Conditions',
            'invalid': 'Terms acceptance must be true'
        }
    )
    accept_privacy = fields.Bool(
        required=True,
        error_messages={
            'required': 'You must accept the Privacy Policy',
            'invalid': 'Privacy policy acceptance must be true'
        }
    )
    
    @validates('accept_terms')
    def validate_accept_terms(self, value):
        """Ensure terms acceptance is explicitly True, not just a boolean."""
        if value is not True:
            raise validate.ValidationError('You must accept the Terms and Conditions')
    
    @validates('accept_privacy')
    def validate_accept_privacy(self, value):
        """Ensure privacy policy acceptance is explicitly True, not just a boolean."""
        if value is not True:
            raise validate.ValidationError('You must accept the Privacy Policy')
    categories = fields.List(
        fields.Str(), # Categories are string keys like 'giving', not integers
        allow_none=True,
        load_default=[],
        error_messages={
            'invalid': 'Categories must be a list of strings'
        }
    )
    subcategories = fields.List(
        fields.Str(), # Subcategories are string keys like 'tithe', not integers
        allow_none=True,
        load_default=[],
        error_messages={
            'invalid': 'Subcategories must be a list of strings'
        }
    )
    custom_category_names = fields.Dict(
        allow_none=True,
        load_default={},
        error_messages={
            'invalid': 'Custom category names must be a dictionary'
        }
    )
    custom_subcategory_names = fields.Dict(
        allow_none=True,
        load_default={},
        error_messages={
            'invalid': 'Custom subcategory names must be a dictionary'
        }
    )
    plan = fields.Str(
        validate=validate.OneOf(['monthly', 'yearly']),
        allow_none=True,
        load_default='monthly',
        error_messages={
            'validator_failed': 'Plan must be either "monthly" or "yearly"'
        }
    )
    
    @pre_load
    def handle_field_names(self, data, **kwargs):
        """Handle both camelCase and snake_case field names."""
        # Map camelCase to snake_case
        field_mapping = {
            'firstName': 'first_name',
            'lastName': 'last_name',
            'preferredName': 'preferred_name',
            'referralSource': 'referral_source',
            'referralDetailsText': 'referral_details',
            'acceptTerms': 'accept_terms',
            'acceptPrivacy': 'accept_privacy'
        }
        
        for camel_case, snake_case in field_mapping.items():
            if camel_case in data and snake_case not in data:
                data[snake_case] = data[camel_case]
        
        # Convert empty strings to None for optional fields
        # This prevents validation errors when empty strings are sent for optional fields
        optional_fields = ['username', 'country', 'preferred_name', 'referral_source', 'referral_details']
        for field in optional_fields:
            if field in data and data[field] == '':
                data[field] = None
        
        return data
    
    @pre_load
    def normalize_categories(self, data, **kwargs):
        """Normalize categories and subcategories - ensure they are lists of strings."""
        # Handle categories - convert from camelCase if needed
        categories_key = 'categories'
        if 'categories' not in data and 'Categories' in data:
            categories_key = 'Categories'
        
        if categories_key in data:
            if isinstance(data[categories_key], list):
                # Keep as strings, just strip whitespace
                normalized = []
                for item in data[categories_key]:
                    if item is None:
                        continue
                    item_str = str(item).strip()
                    if item_str:
                        normalized.append(item_str)
                data['categories'] = normalized
            elif data[categories_key] is None:
                data['categories'] = []
        
        # Handle subcategories - convert from camelCase if needed
        subcategories_key = 'subcategories'
        if 'subcategories' not in data and 'Subcategories' in data:
            subcategories_key = 'Subcategories'
        
        if subcategories_key in data:
            if isinstance(data[subcategories_key], list):
                # Keep as strings, just strip whitespace
                normalized = []
                for item in data[subcategories_key]:
                    if item is None:
                        continue
                    item_str = str(item).strip()
                    if item_str:
                        normalized.append(item_str)
                data['subcategories'] = normalized
            elif data[subcategories_key] is None:
                data['subcategories'] = []
        
        return data
    
    @validates('categories')
    def validate_categories(self, value):
        """Validate categories list."""
        if not isinstance(value, list):
            raise validate.ValidationError('Categories must be a list')
        for item in value:
            if not isinstance(item, str):
                raise validate.ValidationError('All category keys must be strings')
            if not item.strip():
                raise validate.ValidationError('Category keys cannot be empty')
    
    @validates('subcategories')
    def validate_subcategories(self, value):
        """Validate subcategories list."""
        if not isinstance(value, list):
            raise validate.ValidationError('Subcategories must be a list')
        for item in value:
            if not isinstance(item, str):
                raise validate.ValidationError('All subcategory keys must be strings')
            if not item.strip():
                raise validate.ValidationError('Subcategory keys cannot be empty')
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        string_fields = ['username', 'first_name', 'last_name', 'country', 
                        'preferred_name', 'referral_source', 'referral_details']
        for field in string_fields:
            if field in data and data[field]:
                data[field] = escape(str(data[field])).strip()
        return data
    
    @pre_load
    def normalize_email(self, data, **kwargs):
        """Normalize email to lowercase."""
        if 'email' in data and data['email']:
            data['email'] = str(data['email']).strip().lower()
        return data
    
    @validates('password')
    def validate_password(self, password):
        """Custom password validation using existing utility."""
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            raise validate.ValidationError(error_message)
        return password

