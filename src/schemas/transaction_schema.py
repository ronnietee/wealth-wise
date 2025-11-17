"""
Transaction validation schemas.
"""

from marshmallow import Schema, fields, validate, ValidationError, pre_load, EXCLUDE
from markupsafe import escape


class TransactionSchema(Schema):
    """Schema for creating a new transaction."""
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=-999999, max=999999),
        error_messages={
            'required': 'Amount is required',
            'invalid': 'Amount must be a valid number',
            'validator_failed': 'Amount must be between -999999 and 999999'
        }
    )
    subcategory_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'Subcategory ID is required',
            'invalid': 'Subcategory ID must be a valid integer',
            'validator_failed': 'Subcategory ID must be greater than 0'
        }
    )
    description = fields.Str(
        validate=validate.Length(max=255),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Description must be 255 characters or less'
        }
    )
    comment = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True,
        load_default=None,
        error_messages={
            'validator_failed': 'Comment must be 500 characters or less'
        }
    )
    transaction_date = fields.Date(
        allow_none=True,
        load_default=None,
        error_messages={
            'invalid': 'Transaction date must be a valid date (YYYY-MM-DD)'
        }
    )
    
    @pre_load
    def process_amount(self, data, **kwargs):
        """Process amount: make positive expenses negative."""
        if 'amount' in data and data['amount'] is not None:
            try:
                amount = float(data['amount'])
                # Make expenses negative (expenses should be negative values)
                if amount > 0:
                    data['amount'] = -amount
            except (ValueError, TypeError):
                pass  # Let marshmallow handle the error
        return data
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        if 'description' in data and data['description']:
            data['description'] = escape(str(data['description'])).strip()
        if 'comment' in data and data['comment']:
            data['comment'] = escape(str(data['comment'])).strip()
        return data


class TransactionUpdateSchema(Schema):
    """Schema for updating a transaction."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    amount = fields.Float(
        validate=validate.Range(min=-999999, max=999999),
        allow_none=True,
        error_messages={
            'invalid': 'Amount must be a valid number',
            'validator_failed': 'Amount must be between -999999 and 999999'
        }
    )
    subcategory_id = fields.Int(
        validate=validate.Range(min=1),
        allow_none=True,
        error_messages={
            'invalid': 'Subcategory ID must be a valid integer',
            'validator_failed': 'Subcategory ID must be greater than 0'
        }
    )
    description = fields.Str(
        validate=validate.Length(max=255),
        allow_none=True,
        error_messages={
            'validator_failed': 'Description must be 255 characters or less'
        }
    )
    comment = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True,
        error_messages={
            'validator_failed': 'Comment must be 500 characters or less'
        }
    )
    transaction_date = fields.Date(
        allow_none=True,
        error_messages={
            'invalid': 'Transaction date must be a valid date (YYYY-MM-DD)'
        }
    )
    
    @pre_load
    def process_amount(self, data, **kwargs):
        """Process amount: make positive expenses negative."""
        if 'amount' in data and data['amount'] is not None:
            try:
                amount = float(data['amount'])
                if amount > 0:
                    data['amount'] = -amount
            except (ValueError, TypeError):
                pass
        return data
    
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        """Sanitize string fields to prevent XSS."""
        if 'description' in data and data['description']:
            data['description'] = escape(str(data['description'])).strip()
        if 'comment' in data and data['comment']:
            data['comment'] = escape(str(data['comment'])).strip()
        return data

