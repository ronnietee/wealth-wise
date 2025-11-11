# Input Validation Documentation

Complete guide to input validation using Marshmallow schemas in STEWARD.

## Table of Contents

1. [Overview](#overview)
2. [What is Marshmallow?](#what-is-marshmallow)
3. [Implementation Status](#implementation-status)
4. [Schema Reference](#schema-reference)
5. [Usage Examples](#usage-examples)
6. [Error Handling](#error-handling)

---

## Overview

STEWARD uses **Marshmallow** for comprehensive input validation across all API endpoints. This provides:

- ✅ **Type validation and coercion**: Automatic conversion of strings to numbers, dates, etc.
- ✅ **Length limits**: Prevents DoS attacks via extremely long strings
- ✅ **Range validation**: Ensures amounts and IDs are within valid ranges
- ✅ **XSS prevention**: Automatic HTML/script tag escaping using `markupsafe.escape`
- ✅ **Consistent error messages**: User-friendly validation error messages
- ✅ **Centralized validation**: All validation logic in one place

---

## What is Marshmallow?

Marshmallow is a Python library that provides:

- **Schema-based validation**: Define data structures with types, constraints, and validation rules
- **Automatic type coercion**: Converts strings to numbers, dates, etc.
- **Deserialization**: Validates and converts JSON → Python objects
- **Serialization**: Converts Python objects → JSON
- **Error handling**: Provides detailed validation error messages

### Benefits

1. **Security**: Prevents XSS, SQL injection, and DoS attacks
2. **Consistency**: Same validation rules across all endpoints
3. **Maintainability**: Centralized validation logic
4. **User Experience**: Clear, specific error messages

---

## Implementation Status

### ✅ Fully Implemented

All API endpoints now use Marshmallow schemas:

- ✅ **Transactions** - Create and update validation
- ✅ **Categories** - Category and subcategory validation
- ✅ **Budgets** - Budget period, allocations, and income sources
- ✅ **Accounts** - Account creation and updates
- ✅ **User/Onboarding** - Onboarding form and contact form
- ✅ **Recurring** - Recurring income and allocations (with period_type)

### Schema Files

All schemas are in `src/schemas/`:
- `transaction_schema.py` - Transaction validation
- `category_schema.py` - Category validation
- `budget_schema.py` - Budget validation
- `account_schema.py` - Account validation
- `user_schema.py` - User/onboarding validation

---

## Schema Reference

### Transaction Schemas

**TransactionSchema** (Create):
- `amount`: Float, required, range: -999999 to 999999
- `subcategory_id`: Integer, required, min: 1
- `description`: String, optional, max: 255 chars
- `comment`: String, optional, max: 500 chars
- `transaction_date`: Date, optional
- Auto-converts positive expenses to negative

**TransactionUpdateSchema** (Update):
- Same fields as TransactionSchema, all optional
- Partial updates supported

### Category Schemas

**CategorySchema** (Create):
- `name`: String, required, 1-100 chars
- XSS sanitization applied

**SubcategorySchema** (Create):
- `name`: String, required, 1-100 chars
- `category_id`: Integer, required, min: 1
- XSS sanitization applied

### Budget Schemas

**BudgetPeriodSchema** (Create):
- `name`: String, required, 1-100 chars
- `period_type`: String, required, one of: monthly, quarterly, yearly, custom
- `start_date`: Date, required, format: YYYY-MM-DD
- `end_date`: Date, required, format: YYYY-MM-DD
- Handles multiple date formats (ISO, MM/DD/YYYY, etc.)
- XSS sanitization applied

**BudgetAllocationsUpdateSchema**:
- `allocations`: List of allocation objects
- Each allocation:
  - `subcategory_id`: Integer, required, min: 1
  - `allocated`: Float, required, min: 0, max: 999999999

### Account Schemas

**AccountSchema** (Create):
- `name`: String, required, 1-100 chars
- `account_type`: String, required, one of: checking, savings, credit, investment, cash, other
- `bank_name`: String, optional, max: 100 chars
- `account_number`: String, optional, max: 50 chars
- `current_balance`: Float, optional, range: -999999999 to 999999999
- XSS sanitization applied

### User/Onboarding Schemas

**OnboardingSchema**:
- `password`: String, required, min: 12 chars, complexity requirements
- `email`: String, required, email format, normalized to lowercase
- `categories`: List of strings (category keys)
- `subcategories`: List of strings (subcategory keys)
- XSS sanitization applied
- Handles camelCase to snake_case conversion

**ContactFormSchema**:
- `name`: String, required, 1-100 chars
- `email`: String, required, email format
- `message`: String, required, 1-1000 chars
- XSS sanitization applied

---

## Usage Examples

### Basic Usage

```python
from ...schemas import TransactionSchema
from ...utils.validation import handle_validation_error

@route('/api/transactions', methods=['POST'])
def create_transaction():
    schema = TransactionSchema()
    
    try:
        validated_data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return handle_validation_error(err)
    
    # Use validated_data (all types are correct, sanitized, validated)
    amount = validated_data['amount']  # Already a float
    description = validated_data.get('description')  # Already sanitized
```

### Error Response Format

```json
{
  "message": "Validation error",
  "errors": {
    "amount": ["Amount must be between -999999 and 999999"],
    "subcategory_id": ["Subcategory ID is required"]
  }
}
```

---

## Error Handling

### Frontend Error Display

The frontend automatically displays validation errors:

```javascript
fetch('/api/transactions', {
    method: 'POST',
    body: JSON.stringify(data)
})
.then(response => {
    if (!response.ok) {
        return response.json().then(err => Promise.reject(err));
    }
    return response.json();
})
.catch(error => {
    if (error.errors) {
        // Display field-specific errors
        for (const [field, messages] of Object.entries(error.errors)) {
            console.error(`${field}: ${messages.join(', ')}`);
        }
    }
});
```

---

## XSS Prevention

All string fields are automatically sanitized using `markupsafe.escape`:

```python
@pre_load
def sanitize_strings(self, data, **kwargs):
    """Sanitize string fields to prevent XSS."""
    if 'description' in data and data['description']:
        data['description'] = escape(str(data['description'])).strip()
    return data
```

This prevents:
- HTML injection
- Script injection
- XSS attacks

---

## Date Handling

Budget schemas handle multiple date formats:

- ISO format: `2024-01-15`
- US format: `01/15/2024`
- ISO datetime: `2024-01-15T10:30:00Z`
- Date objects: Automatically converted

All dates are normalized to `YYYY-MM-DD` format.

---

## Field Name Conversion

Schemas automatically handle camelCase to snake_case conversion:

```python
@pre_load
def handle_field_names(self, data, **kwargs):
    """Handle both camelCase and snake_case field names."""
    if 'startDate' in data and 'start_date' not in data:
        data['start_date'] = data['startDate']
    return data
```

---

## Best Practices

1. **Always use schemas** for API endpoints that accept user input
2. **Handle ValidationError** using `handle_validation_error()` utility
3. **Provide clear error messages** in schema field definitions
4. **Sanitize strings** using the `@pre_load` sanitize_strings method
5. **Validate ranges** to prevent DoS attacks
6. **Use `unknown = EXCLUDE`** in Meta class to ignore extra fields

---

**Last Updated:** January 2025  
**Status:** Fully implemented across all endpoints ✅

