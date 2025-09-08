# Wealth Wise Development Log

## Project Overview
**Wealth Wise** - A Christian family budgeting and financial tracking web application built with Flask, SQLite, and vanilla HTML/CSS/JavaScript.

## Current Status: PARTIALLY WORKING
- ✅ Core functionality implemented
- ❌ Database schema issues causing errors
- ❌ Month management temporarily disabled
- ❌ Some features need debugging

## Completed Features

### 1. User Authentication
- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Improved error handling for signup

### 2. Database Models
- ✅ User model with currency preference
- ✅ Category and Subcategory models
- ✅ Transaction model for expenses
- ✅ Budget model (simplified version)
- ✅ IncomeSource model for multiple income streams
- ✅ BudgetAllocation model for fund allocation

### 3. Core Pages
- ✅ Landing page with login/signup
- ✅ Dashboard with financial overview
- ✅ Income management page
- ✅ Breakdown page (categories/subcategories)
- ✅ Input page for expense tracking
- ✅ Summary page
- ✅ Settings page
- ✅ Transactions page with edit/delete

### 4. API Endpoints
- ✅ User authentication APIs
- ✅ Budget management APIs
- ✅ Income source management APIs
- ✅ Category/subcategory management APIs
- ✅ Transaction management APIs
- ✅ User settings APIs
- ✅ Password change API

### 5. UI/UX Improvements
- ✅ Responsive modal dialogs
- ✅ Currency display (ZAR, USD, etc.)
- ✅ Sticky allocation summary on breakdown page
- ✅ Compact layout with better input sizing
- ✅ Quick actions on dashboard
- ✅ Beautiful, cozy design theme
- ✅ Mobile-compatible interface

### 6. Advanced Features
- ✅ Multiple income sources support
- ✅ Balance brought forward functionality
- ✅ Allocation validation (prevents over-allocation)
- ✅ Transaction history with filtering
- ✅ Category/subcategory editing and deletion
- ✅ Real-time balance calculations

## Current Issues

### 1. Database Schema Problems
- ❌ **CRITICAL**: Database still references non-existent columns (`budget.month`, `budget.year`, `budget.is_active`)
- ❌ Error: `sqlalchemy.exc.OperationalError: no such column: budget.month`
- ❌ This prevents the application from running properly

### 2. Month Management
- ❌ Month selector functionality disabled due to database issues
- ❌ Cannot switch between different months
- ❌ Cannot start new months with balance carry-forward

### 3. Potential Issues
- ❌ Some API endpoints may still reference removed columns
- ❌ Frontend JavaScript may have references to removed month fields

## Files Structure
```
wealth-wise/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       ├── main.js       # Core JavaScript functions
│       └── auth.js       # Authentication JavaScript
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── dashboard.html    # Dashboard page
│   ├── income.html       # Income management
│   ├── breakdown.html    # Categories/subcategories
│   ├── input.html        # Expense input
│   ├── summary.html      # Financial summary
│   ├── settings.html     # User settings
│   └── transactions.html # Transaction history
└── instance/
    └── wealthwise.db     # SQLite database
```

## Next Steps to Fix

### 1. Immediate Fixes (Priority 1)
1. **Fix Database Schema Issues**
   - Remove all references to `month`, `year`, `is_active` columns
   - Ensure all API endpoints work with simplified Budget model
   - Test all functionality after schema fix

2. **Test Core Functionality**
   - Verify signup/login works
   - Test income source management
   - Test category/subcategory management
   - Test expense tracking
   - Test transaction editing

### 2. Future Enhancements (Priority 2)
1. **Implement Month Management Properly**
   - Add proper database migration for month/year fields
   - Implement month selector UI
   - Add balance carry-forward logic
   - Test month switching functionality

2. **Additional Features**
   - Export functionality
   - Reports and analytics
   - Budget templates
   - Recurring transactions

## Technical Details

### Database Schema (Current)
```sql
-- Users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE category (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL,
    is_template BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Subcategories table
CREATE TABLE subcategory (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category (id)
);

-- Transactions table
CREATE TABLE transaction (
    id INTEGER PRIMARY KEY,
    amount FLOAT NOT NULL,
    description VARCHAR(200),
    comment TEXT,
    subcategory_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subcategory_id) REFERENCES subcategory (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Budget table (simplified)
CREATE TABLE budget (
    id INTEGER PRIMARY KEY,
    month_year VARCHAR(7) NOT NULL,
    total_income FLOAT DEFAULT 0,
    balance_brought_forward FLOAT DEFAULT 0,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Income sources table
CREATE TABLE income_source (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL,
    budget_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budget (id)
);

-- Budget allocations table
CREATE TABLE budget_allocation (
    id INTEGER PRIMARY KEY,
    allocated_amount FLOAT DEFAULT 0,
    subcategory_id INTEGER NOT NULL,
    budget_id INTEGER NOT NULL,
    FOREIGN KEY (subcategory_id) REFERENCES subcategory (id),
    FOREIGN KEY (budget_id) REFERENCES budget (id)
);
```

### Key Dependencies
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-CORS==4.0.0
python-dotenv==1.0.0
bcrypt==4.0.1
PyJWT==2.8.0
```

## Development Commands

### Start Application
```bash
cd C:\Users\jtste\wealth-wise
python app.py
```

### Create Fresh Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Delete Database (if needed)
```bash
del instance\wealthwise.db
```

## Contact & Support
- Application URL: http://localhost:5000
- Database: SQLite (instance/wealthwise.db)
- Framework: Flask with SQLAlchemy ORM
- Frontend: Vanilla HTML/CSS/JavaScript

## Notes
- The application was working with a simplified Budget model
- Month management was temporarily disabled due to database schema conflicts
- All core budgeting features are implemented and should work once database issues are resolved
- The application follows a mobile-first, responsive design approach
- All monetary values respect the user's selected currency preference

---
**Last Updated**: September 7, 2025
**Status**: Needs database schema fixes before full functionality
