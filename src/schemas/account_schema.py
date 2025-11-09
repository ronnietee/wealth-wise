"""
Account validation schemas.
"""

from marshmallow import Schema, fields, validate, pre_load, EXCLUDE
from markupsafe import escape


class AccountSchema(Schema):
    """Schema for creating a new account."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Account name is required',
            'validator_failed': 'Account name must be between 1 and 100 characters'
        }
    )
    account_type = fields.Str(
        required=True,
        validate=validate.OneOf(['checking', 'savings', 'credit', 'investment', 'cash', 'other']),
        error_messages={
            'required': 'Account type is required',
            'validator_failed': 'Account type must be one of: checking, savings, credit, investment, cash, other'
        }
    )
    bank_name = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Bank name must be 100 characters or less'
        }
    )
    account_number = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Account number must be 50 characters or less'
        }
    )
    current_balance = fields.Float(
        validate=validate.Range(min=-999999999, max=999999999),
        load_default=0.0,
        error_messages={
            'invalid': 'Current balance must be a valid number',
            'validator_failed': 'Current balance must be between -999999999 and 999999999'
        }
    )
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        for field in ['name', 'bank_name', 'account_number']:
            if field in data and data[field]:
                data[field] = escape(str(data[field])).strip()
        return data


class AccountUpdateSchema(Schema):
    """Schema for updating an account."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    name = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True,
        error_messages={
            'validator_failed': 'Account name must be between 1 and 100 characters'
        }
    )
    account_type = fields.Str(
        validate=validate.OneOf(['checking', 'savings', 'credit', 'investment', 'cash', 'other']),
        allow_none=True,
        error_messages={
            'validator_failed': 'Account type must be one of: checking, savings, credit, investment, cash, other'
        }
    )
    bank_name = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        error_messages={
            'validator_failed': 'Bank name must be 100 characters or less'
        }
    )
    account_number = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True,
        error_messages={
            'validator_failed': 'Account number must be 50 characters or less'
        }
    )
    current_balance = fields.Float(
        validate=validate.Range(min=-999999999, max=999999999),
        allow_none=True,
        error_messages={
            'invalid': 'Current balance must be a valid number',
            'validator_failed': 'Current balance must be between -999999999 and 999999999'
        }
    )
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        for field in ['name', 'bank_name', 'account_number']:
            if field in data and data[field]:
                data[field] = escape(str(data[field])).strip()
        return data

