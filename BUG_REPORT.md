# Wealth Wise Bug Report

## Critical Issues (Must Fix)

### 1. Database Schema Mismatch
**Status**: 🔴 CRITICAL
**Error**: `sqlalchemy.exc.OperationalError: no such column: budget.month`
**Location**: Multiple API endpoints
**Description**: The code references columns that don't exist in the database schema

**Affected Endpoints**:
- `/api/budget` (GET)
- `/api/categories` (GET)
- Any endpoint that queries the Budget model

**Root Cause**: 
- Code was updated to include `month`, `year`, and `is_active` columns
- Database was not properly migrated to include these columns
- Model definition and actual database schema are out of sync

**Fix Required**:
1. Remove all references to non-existent columns from the code
2. Ensure Budget model matches actual database schema
3. Test all API endpoints

### 2. Application Won't Start
**Status**: 🔴 CRITICAL
**Error**: Application crashes on startup due to database errors
**Description**: Cannot access the application at all

**Fix Required**:
1. Fix database schema issues first
2. Ensure application starts without errors
3. Verify all pages load correctly

## High Priority Issues

### 3. Month Management Disabled
**Status**: 🟡 HIGH
**Description**: Month selector and month switching functionality is disabled
**Impact**: Users cannot manage different months or carry forward balances

**Fix Required**:
1. Implement proper database migration for month management
2. Add month/year columns to Budget table
3. Implement month switching logic
4. Add month selector UI back

### 4. Potential API Endpoint Issues
**Status**: 🟡 HIGH
**Description**: Some API endpoints may still reference removed columns
**Impact**: Could cause 500 errors when using certain features

**Endpoints to Check**:
- `/api/budget` (PUT)
- `/api/allocations` (POST)
- Any endpoint that creates or updates budgets

## Medium Priority Issues

### 5. Frontend JavaScript References
**Status**: 🟡 MEDIUM
**Description**: JavaScript may reference removed month fields
**Impact**: Could cause JavaScript errors in browser console

**Files to Check**:
- `templates/base.html` (month selector JavaScript)
- Any JavaScript that references `budget.month` or `budget.year`

### 6. Currency Display Consistency
**Status**: 🟡 MEDIUM
**Description**: Some parts of the app may not respect user's currency setting
**Impact**: Inconsistent currency display across the application

## Low Priority Issues

### 7. Error Handling
**Status**: 🟢 LOW
**Description**: Some error messages could be more user-friendly
**Impact**: Users may see technical error messages

### 8. UI Polish
**Status**: 🟢 LOW
**Description**: Some UI elements could be more polished
**Impact**: Minor user experience issues

## Testing Checklist

### After Fixing Database Issues
- [ ] Application starts without errors
- [ ] User can sign up for new account
- [ ] User can log in
- [ ] Dashboard loads and shows correct data
- [ ] Income page works (add/edit/delete income sources)
- [ ] Breakdown page loads categories
- [ ] Can add/edit/delete categories and subcategories
- [ ] Can allocate funds to subcategories
- [ ] Input page works (add expenses)
- [ ] Transactions page shows transaction history
- [ ] Can edit/delete transactions
- [ ] Settings page works (currency, password change)
- [ ] All monetary values show in selected currency

### After Implementing Month Management
- [ ] Month selector appears in navigation
- [ ] Can switch between different months
- [ ] Can start new month with balance carry-forward
- [ ] Data is properly separated by month
- [ ] Month switching updates all pages correctly

## Quick Fix Commands

### Reset Database
```bash
cd C:\Users\jtste\wealth-wise
del instance\wealthwise.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Start Application
```bash
python app.py
```

### Check Application Status
```bash
curl http://localhost:5000
```

## Files That Need Attention

1. **app.py** - Remove references to non-existent columns
2. **templates/base.html** - Remove month selector JavaScript
3. **static/js/main.js** - Check for month field references
4. **Database schema** - Ensure consistency between model and actual database

---
**Report Generated**: September 7, 2025
**Priority**: Fix database schema issues first, then test all functionality
