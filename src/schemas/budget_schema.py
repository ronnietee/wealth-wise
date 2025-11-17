"""
Budget validation schemas.
"""

from marshmallow import Schema, fields, validate, pre_load
from markupsafe import escape
from datetime import datetime


class BudgetPeriodSchema(Schema):
    """Schema for creating a new budget period."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Budget period name is required',
            'validator_failed': 'Budget period name must be between 1 and 100 characters'
        }
    )
    period_type = fields.Str(
        required=True,
        validate=validate.OneOf(['monthly', 'quarterly', 'yearly', 'custom']),
        error_messages={
            'required': 'Period type is required',
            'validator_failed': 'Period type must be one of: monthly, quarterly, yearly, custom'
        }
    )
    start_date = fields.Date(
        required=True,
        error_messages={
            'required': 'Start date is required',
            'invalid': 'Start date must be a valid date (YYYY-MM-DD)'
        }
    )
    end_date = fields.Date(
        required=True,
        error_messages={
            'required': 'End date is required',
            'invalid': 'End date must be a valid date (YYYY-MM-DD)'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data
    
    @pre_load
    def handle_field_names(self, data, **kwargs):
        """Handle both camelCase and snake_case field names."""
        # Map camelCase to snake_case for dates
        if 'startDate' in data and 'start_date' not in data:
            data['start_date'] = data['startDate']
        if 'endDate' in data and 'end_date' not in data:
            data['end_date'] = data['endDate']
        return data
    
    @pre_load
    def parse_dates(self, data, **kwargs):
        """Normalize date strings to YYYY-MM-DD format for Marshmallow."""
        for date_field in ['start_date', 'end_date']:
            if date_field in data and data[date_field]:
                try:
                    date_value = data[date_field]
                    
                    # If it's already a date object, convert to string
                    if isinstance(date_value, datetime):
                        data[date_field] = date_value.date().isoformat()
                        continue
                    elif hasattr(date_value, 'date'):  # datetime.date object
                        data[date_field] = date_value.isoformat()
                        continue
                    
                    # Convert to string
                    date_str = str(date_value).strip()
                    
                    # If it's already in YYYY-MM-DD format, keep it
                    if len(date_str) == 10 and date_str.count('-') == 2:
                        # Validate it's a valid date format
                        try:
                            datetime.strptime(date_str, '%Y-%m-%d')
                            # Already in correct format, keep it
                            continue
                        except ValueError:
                            pass
                    
                    # Try ISO format with or without timezone
                    if 'T' in date_str or 'Z' in date_str:
                        date_str = date_str.replace('Z', '+00:00')
                        try:
                            if '+' in date_str or date_str.count('-') > 2:
                                # Has timezone info
                                parsed = datetime.fromisoformat(date_str)
                                data[date_field] = parsed.date().isoformat()
                            else:
                                # ISO format without timezone
                                parsed = datetime.fromisoformat(date_str)
                                data[date_field] = parsed.date().isoformat()
                            continue
                        except (ValueError, AttributeError):
                            pass
                    
                    # Try other common formats
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            parsed = datetime.strptime(date_str, fmt)
                            data[date_field] = parsed.date().isoformat()
                            break
                        except ValueError:
                            continue
                    # If all formats fail, let marshmallow handle it
                except (ValueError, AttributeError, TypeError) as e:
                    # Let marshmallow handle the error with a better message
                    pass
        return data


class BudgetPeriodUpdateSchema(Schema):
    """Schema for updating a budget period."""
    name = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True,
        error_messages={
            'validator_failed': 'Budget period name must be between 1 and 100 characters'
        }
    )
    period_type = fields.Str(
        validate=validate.OneOf(['monthly', 'quarterly', 'yearly', 'custom']),
        allow_none=True,
        error_messages={
            'validator_failed': 'Period type must be one of: monthly, quarterly, yearly, custom'
        }
    )
    start_date = fields.Date(
        allow_none=True,
        error_messages={
            'invalid': 'Start date must be a valid date (YYYY-MM-DD)'
        }
    )
    end_date = fields.Date(
        allow_none=True,
        error_messages={
            'invalid': 'End date must be a valid date (YYYY-MM-DD)'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data
    
    @pre_load
    def handle_field_names(self, data, **kwargs):
        """Handle both camelCase and snake_case field names."""
        # Map camelCase to snake_case for dates
        if 'startDate' in data and 'start_date' not in data:
            data['start_date'] = data['startDate']
        if 'endDate' in data and 'end_date' not in data:
            data['end_date'] = data['endDate']
        return data
    
    @pre_load
    def parse_dates(self, data, **kwargs):
        """Normalize date strings to YYYY-MM-DD format for Marshmallow."""
        for date_field in ['start_date', 'end_date']:
            if date_field in data and data[date_field]:
                try:
                    date_value = data[date_field]
                    
                    # If it's already a date object, convert to string
                    if isinstance(date_value, datetime):
                        data[date_field] = date_value.date().isoformat()
                        continue
                    elif hasattr(date_value, 'date'):  # datetime.date object
                        data[date_field] = date_value.isoformat()
                        continue
                    
                    # Convert to string
                    date_str = str(date_value).strip()
                    
                    # If it's already in YYYY-MM-DD format, keep it
                    if len(date_str) == 10 and date_str.count('-') == 2:
                        # Validate it's a valid date format
                        try:
                            datetime.strptime(date_str, '%Y-%m-%d')
                            # Already in correct format, keep it
                            continue
                        except ValueError:
                            pass
                    
                    # Try ISO format with or without timezone
                    if 'T' in date_str or 'Z' in date_str:
                        date_str = date_str.replace('Z', '+00:00')
                        try:
                            if '+' in date_str or date_str.count('-') > 2:
                                # Has timezone info
                                parsed = datetime.fromisoformat(date_str)
                                data[date_field] = parsed.date().isoformat()
                            else:
                                # ISO format without timezone
                                parsed = datetime.fromisoformat(date_str)
                                data[date_field] = parsed.date().isoformat()
                            continue
                        except (ValueError, AttributeError):
                            pass
                    
                    # Try other common formats
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            parsed = datetime.strptime(date_str, fmt)
                            data[date_field] = parsed.date().isoformat()
                            break
                        except ValueError:
                            continue
                    # If all formats fail, let marshmallow handle it
                except (ValueError, AttributeError, TypeError) as e:
                    # Let marshmallow handle the error with a better message
                    pass
        return data


class BudgetUpdateSchema(Schema):
    """Schema for updating budget details."""
    total_income = fields.Float(
        validate=validate.Range(min=0, max=999999999),
        allow_none=True,
        error_messages={
            'invalid': 'Total income must be a valid number',
            'validator_failed': 'Total income must be between 0 and 999999999'
        }
    )
    balance_brought_forward = fields.Float(
        validate=validate.Range(min=-999999999, max=999999999),
        allow_none=True,
        error_messages={
            'invalid': 'Balance brought forward must be a valid number',
            'validator_failed': 'Balance brought forward must be between -999999999 and 999999999'
        }
    )


class BudgetAllocationSchema(Schema):
    """Schema for a single budget allocation."""
    subcategory_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'Subcategory ID is required',
            'invalid': 'Subcategory ID must be a valid integer',
            'validator_failed': 'Subcategory ID must be greater than 0'
        }
    )
    allocated = fields.Float(
        required=True,
        validate=validate.Range(min=0, max=999999999),
        error_messages={
            'required': 'Allocated amount is required',
            'invalid': 'Allocated amount must be a valid number',
            'validator_failed': 'Allocated amount must be between 0 and 999999999'
        }
    )


class BudgetAllocationsUpdateSchema(Schema):
    """Schema for updating multiple budget allocations."""
    allocations = fields.List(
        fields.Nested(BudgetAllocationSchema),
        required=True,
        validate=validate.Length(min=0),
        error_messages={
            'required': 'Allocations list is required',
            'invalid': 'Allocations must be a list',
            'validator_failed': 'Allocations must be a valid list'
        }
    )


class IncomeSourceSchema(Schema):
    """Schema for creating an income source."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Income source name is required',
            'validator_failed': 'Income source name must be between 1 and 100 characters'
        }
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0, max=999999999),
        error_messages={
            'required': 'Amount is required',
            'invalid': 'Amount must be a valid number',
            'validator_failed': 'Amount must be between 0 and 999999999'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data


class IncomeSourceUpdateSchema(Schema):
    """Schema for updating an income source."""
    name = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True,
        error_messages={
            'validator_failed': 'Income source name must be between 1 and 100 characters'
        }
    )
    amount = fields.Float(
        validate=validate.Range(min=0, max=999999999),
        allow_none=True,
        error_messages={
            'invalid': 'Amount must be a valid number',
            'validator_failed': 'Amount must be between 0 and 999999999'
        }
    )
    
    @pre_load
    def sanitize_name(self, data, **kwargs):
        """Sanitize name to prevent XSS."""
        if 'name' in data and data['name']:
            data['name'] = escape(str(data['name'])).strip()
        return data

