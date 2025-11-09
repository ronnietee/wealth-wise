# Marshmallow Input Validation Implementation

## Overview

Full Marshmallow schema-based input validation has been implemented across all API endpoints. This provides:
- **Type validation and coercion**: Automatic conversion of strings to numbers, dates, etc.
- **Length limits**: Prevents DoS attacks via extremely long strings
- **Range validation**: Ensures amounts and IDs are within valid ranges
- **XSS prevention**: Automatic HTML/script tag escaping using `markupsafe.escape`
- **Consistent error messages**: User-friendly validation error messages
- **Centralized validation**: All validation logic in one place

## Implementation Details

### Schemas Created

1. **TransactionSchema** (`src/schemas/transaction_schema.py`)
   - Validates transaction creation
   - Amount: -999999 to 999999
   - Description: max 255 characters
   - Comment: max 500 characters
   - Automatically makes positive expenses negative

2. **TransactionUpdateSchema**
   - Partial validation for updates
   - Same constraints as TransactionSchema

3. **CategorySchema** (`src/schemas/category_schema.py`)
   - Name: 1-100 characters
   - XSS sanitization

4. **SubcategorySchema**
   - Name: 1-100 characters
   - Category ID: must be > 0
   - XSS sanitization

5. **BudgetPeriodSchema** (`src/schemas/budget_schema.py`)
   - Name: 1-100 characters
   - Period type: monthly, yearly, or custom
   - Date validation and parsing
   - XSS sanitization

6. **BudgetUpdateSchema**
   - Total income: 0 to 999999999
   - Balance brought forward: -999999999 to 999999999

7. **BudgetAllocationsUpdateSchema**
   - Validates list of allocations
   - Each allocation: subcategory_id > 0, allocated >= 0

8. **IncomeSourceSchema**
   - Name: 1-100 characters
   - Amount: 0 to 999999999
   - XSS sanitization

9. **AccountSchema** (`src/schemas/account_schema.py`)
   - Name: 1-100 characters
   - Account type: checking, savings, credit, investment, other
   - Bank name: max 100 characters
   - Account number: max 50 characters
   - Current balance: -999999999 to 999999999
   - XSS sanitization

10. **OnboardingSchema** (`src/schemas/user_schema.py`)
    - Email: valid email format, max 255 characters
    - Password: 12+ characters, validated with existing password strength utility
    - First/Last name: 1-100 characters
    - Optional fields: country, preferred_name, referral_source, referral_details
    - Legal acceptance: terms and privacy policy (required)
    - Categories/subcategories: lists of integers
    - Custom category/subcategory names: dictionaries
    - Plan: monthly or yearly
    - Handles both camelCase and snake_case field names
    - XSS sanitization

11. **ContactFormSchema**
    - Name: 1-100 characters
    - Email: valid email format
    - Subject: 1-200 characters
    - Message: 1-2000 characters
    - XSS sanitization

### Updated Route Handlers

All API route handlers have been updated to use schemas:

- `src/routes/api/transactions.py`: TransactionSchema, TransactionUpdateSchema
- `src/routes/api/categories.py`: CategorySchema, SubcategorySchema, CategoryUpdateSchema, SubcategoryUpdateSchema
- `src/routes/api/budget.py`: BudgetPeriodSchema, BudgetPeriodUpdateSchema, BudgetUpdateSchema, BudgetAllocationsUpdateSchema, IncomeSourceSchema, IncomeSourceUpdateSchema
- `src/routes/api/accounts.py`: AccountSchema, AccountUpdateSchema
- `src/routes/api/__init__.py`: OnboardingSchema, ContactFormSchema

### Utility Functions

**`src/utils/validation.py`**
- `handle_validation_error()`: Converts Marshmallow ValidationError to Flask JSON response
- Provides user-friendly error messages

## Security Features

1. **XSS Prevention**: All string fields are automatically escaped using `markupsafe.escape`
2. **Length Limits**: Prevents DoS attacks via extremely long strings
3. **Range Validation**: Prevents invalid data (negative IDs, out-of-range amounts)
4. **Type Coercion**: Automatic type conversion prevents type-related errors
5. **Required Field Validation**: Ensures all required fields are present

## Error Handling

Validation errors return:
- **Status Code**: 400 (Bad Request)
- **Response Format**:
  ```json
  {
    "message": "First error message",
    "errors": {
      "field_name": ["Error message 1", "Error message 2"]
    }
  }
  ```

## Usage Example

### Before (Manual Validation)
```python
data = request.get_json()
amount = data.get('amount')
if not amount:
    return jsonify({'message': 'Amount is required'}), 400
try:
    amount = float(amount)
except (ValueError, TypeError):
    return jsonify({'message': 'Invalid amount'}), 400
```

### After (Marshmallow Schema)
```python
schema = TransactionSchema()
try:
    validated_data = schema.load(request.get_json() or {})
except ValidationError as err:
    return handle_validation_error(err)

# validated_data['amount'] is guaranteed to be:
# - A float
# - Between -999999 and 999999
# - Present (required field)
```

## Testing

To test the validation:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test with invalid data**:
   ```bash
   curl -X POST http://localhost:5000/api/transactions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"amount": "invalid", "subcategory_id": -1}'
   ```
   
   Should return:
   ```json
   {
     "message": "Amount must be a valid number",
     "errors": {
       "amount": ["Amount must be a valid number"],
       "subcategory_id": ["Subcategory ID must be greater than 0"]
     }
   }
   ```

3. **Test with valid data**:
   ```bash
   curl -X POST http://localhost:5000/api/transactions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"amount": 100.50, "subcategory_id": 1, "description": "Test transaction"}'
   ```
   
   Should return 201 with transaction data.

## Benefits

1. **Consistency**: All endpoints validate data the same way
2. **Maintainability**: Validation logic centralized in schemas
3. **Security**: XSS prevention, length limits, range validation
4. **User Experience**: Clear, specific error messages
5. **Type Safety**: Automatic type coercion prevents errors
6. **Documentation**: Schemas serve as documentation for API contracts

## Future Enhancements

Potential improvements:
- Add custom validators for business logic (e.g., date ranges)
- Add schema serialization for API documentation
- Add validation for nested objects
- Add conditional validation (e.g., if account_type is 'credit', require credit_limit)

