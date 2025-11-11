# STEWARD - Christian Family Budgeting Tool

A comprehensive, mobile-friendly budgeting application designed specifically for Christian families to steward their finances with wisdom and faith.

## Features

- **Faith-Based Categories**: Pre-configured with Christian values including tithe, offering, and social responsibility
- **Budget Periods**: Create and manage monthly or custom budget periods
- **Recurring Income & Allocations**: Set up recurring income sources and budget allocations that auto-populate
- **Transaction Tracking**: Record income and expenses with detailed categorization
- **Dashboard Overview**: Real-time financial overview with spending progress and alerts
- **Account Management**: Link and manage multiple bank accounts
- **Mobile Responsive**: Works perfectly on all devices
- **Beautiful UI**: Modern design with dark/light theme support
- **Email Verification**: Secure account creation with email verification
- **Password Management**: Secure password reset functionality
- **Data Export**: Export your financial data to Excel for record keeping

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: JWT-based token authentication
- **Email**: Flask-Mail for email verification and password reset
- **Data Export**: openpyxl for Excel exports

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- PostgreSQL (for production)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wealth-wise
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy `env.example` to `.env` and update with your values:
   ```bash
   cp env.example .env
   ```
   
   **Generate admin password hash:**
   ```bash
   python generate_admin_password.py
   ```
   This will prompt you for a password and generate a secure hash. Copy the output and add it to your `.env` file as `ADMIN_PASSWORD_HASH`.
   
   **Required variables:**
   - `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `JWT_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `ADMIN_PASSWORD_HASH` - Generate with: `python generate_admin_password.py`
   - `ADMIN_USERNAME` - Admin username (default: `admin`)
   
   See `env.example` for all available configuration options.

5. **Initialize the database**
   ```bash
   python -m flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Usage

### Getting Started

1. **Sign Up**: Create a new account with your email and password
2. **Onboarding**: Complete the onboarding process to set up your categories
3. **Create Budget Period**: Set up your first budget period (monthly, quarterly, etc.)
4. **Add Income**: Enter your income sources for the period
5. **Allocate Budget**: Distribute your available funds across categories
6. **Track Expenses**: Record transactions and monitor spending
7. **Monitor Progress**: Use the dashboard to track your financial health

### Key Features Explained

#### Budget Periods
- Create custom budget periods (monthly, quarterly, annual, etc.)
- Set start and end dates for each period
- Only one active period at a time
- Activate/deactivate periods as needed

#### Recurring Income & Allocations
- Set up recurring income sources that auto-populate in new periods
- Set recurring allocations to auto-allocate to categories
- Saves time setting up new budget periods

#### Transaction Management
- Record income (positive amounts) and expenses (negative amounts)
- Categorize by category and subcategory
- Add comments and descriptions
- Edit and delete transactions

#### Dashboard Insights
- Total Income: Sum of all income sources
- Balance: Remaining available funds
- Allocated: Total allocated to categories
- Spent: Total expenses tracked
- Progress Bar: Visual spending indicator
- Overspending Alerts: Warnings when over budget

### Onboarding Categories

The application includes these default categories during onboarding:

- **Giving**: Tithe, Offering, Social Responsibility
- **Groceries**: Food & Home Essentials, Dining out
- **Housing**: Mortgage/Rent, HOA Fees, Electricity, Water, Home Insurance, Internet
- **Transportation**: Loan repayment, Insurance, Fuel, Car Tracker, Car wash
- **Monthly Commitments**: Life cover, Funeral Plan, Credit card repayment, Banking Fees
- **Leisure/Entertainment**: Spotify, Weekend adventures
- **Personal Care**: Gym membership, Haircuts, Clothing
- **Savings Goals**: Emergency fund, General Savings, Short term goals
- **Once-off expenses**: Asset purchase, Emergency

You can add custom categories and subcategories as needed.

## Project Structure

```
wealth-wise/
├── app.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variable template
├── src/                         # Modular source code
│   ├── __init__.py             # Application factory
│   ├── config/                  # Configuration management
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── budget.py           # Budget models
│   │   ├── category.py          # Category models
│   │   ├── transaction.py       # Transaction model
│   │   ├── account.py           # Account model
│   │   ├── income.py            # Income models
│   │   ├── recurring.py         # Recurring models
│   │   └── auth.py              # Auth tokens
│   ├── routes/                  # Flask blueprints
│   │   ├── main.py             # Main routes
│   │   ├── auth.py             # Authentication routes
│   │   └── api/                # API endpoints
│   │       ├── budget.py       # Budget API
│   │       ├── categories.py   # Categories API
│   │       ├── transactions.py # Transactions API
│   │       ├── accounts.py     # Accounts API
│   │       ├── recurring.py   # Recurring API
│   │       └── user.py         # User API
│   ├── services/                # Business logic
│   │   ├── user_service.py
│   │   ├── budget_service.py
│   │   ├── category_service.py
│   │   ├── transaction_service.py
│   │   ├── account_service.py
│   │   ├── auth_service.py
│   │   └── email_service.py
│   └── utils/                   # Utility functions
│       ├── currency.py         # Currency handling
│       ├── budget.py           # Budget utilities
│       └── email.py            # Email utilities
├── templates/                   # HTML templates
│   ├── base.html              # Base template
│   ├── dashboard.html          # Dashboard page
│   ├── income.html             # Income management
│   ├── breakdown.html          # Budget breakdown
│   ├── transactions.html       # Transaction list
│   ├── accounts.html           # Account management
│   ├── budgets.html            # Budget periods
│   ├── settings.html           # User settings
│   ├── help.html               # Help/guide
│   └── ...
├── static/                      # Static files
│   ├── css/style.css           # Main stylesheet
│   ├── js/                      # JavaScript
│   │   ├── main.js            # Global functions
│   │   ├── auth.js            # Authentication
│   │   └── onboarding.js      # Onboarding flow
│   └── images/                  # Images
│       └── logo.png           # Application logo
├── migrations/                  # Database migrations
├── instance/                    # Database files
└── tests/                       # Test files (if any)
```

## Documentation

For comprehensive documentation, see the [docs/](docs/) directory:

- **[Security Documentation](docs/SECURITY.md)** - Security implementation, audit, and testing
- **[Input Validation](docs/VALIDATION.md)** - Marshmallow schema validation guide
- **[Database Documentation](docs/database/README.md)** - Database structure and optimization
- **[Billing Documentation](docs/billing/README.md)** - Payment system and admin setup
- **[Legal Documents](docs/legal/)** - Terms and conditions, privacy policy

## API Documentation

### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/theme` - Update theme preference

### Budget Management
- `GET /api/budget/budget` - Get active budget
- `PUT /api/budget/budget` - Update budget
- `GET /api/budget/budget-periods` - Get all periods
- `POST /api/budget/budget-periods` - Create period
- `PUT /api/budget/budget-periods/<id>` - Update period
- `POST /api/budget/budget-periods/<id>/activate` - Activate period
- `DELETE /api/budget/budget-periods/<id>` - Delete period
- `POST /api/budget/allocations` - Update allocations
- `POST /api/budget/income-sources` - Add income source
- `PUT /api/budget/income-sources/<id>` - Update income source
- `DELETE /api/budget/income-sources/<id>` - Delete income source
- `POST /api/budget/recalculate-income` - Recalculate income

### Categories
- `GET /api/categories/categories` - Get user categories
- `POST /api/categories/categories` - Create category
- `POST /api/categories/subcategories` - Create subcategory
- `DELETE /api/categories/subcategories/<id>` - Delete subcategory

### Transactions
- `GET /api/transactions/transactions` - Get all transactions
- `POST /api/transactions/transactions` - Create transaction
- `PUT /api/transactions/transactions/<id>` - Update transaction
- `DELETE /api/transactions/transactions/<id>` - Delete transaction

### Accounts
- `GET /api/accounts` - Get all accounts
- `POST /api/accounts` - Create account
- `GET /api/accounts/balance-summary` - Get balance summary

### Recurring
- `GET /api/recurring-income-sources` - Get recurring income
- `POST /api/recurring-income-sources` - Create recurring income
- `PUT /api/recurring-income-sources/<id>` - Update recurring income
- `DELETE /api/recurring-income-sources/<id>` - Delete recurring income
- `GET /api/recurring-allocations` - Get recurring allocations
- `POST /api/recurring-allocations` - Create recurring allocation
- `PUT /api/recurring-allocations/<id>` - Update recurring allocation
- `DELETE /api/recurring-allocations/<id>` - Delete recurring allocation

## Database Schema

### User
- User accounts with authentication
- Email verification status
- Theme preferences
- Currency preferences

### Budget Period
- Budget period definitions
- Active/inactive status
- Start and end dates

### Budget
- Total income
- Balance brought forward
- Links to income sources and allocations

### Income Source
- Income entries
- Recurring income tracking
- Links to budget periods

### Category & Subcategory
- User-defined categories
- Category hierarchy
- Template vs custom

### Budget Allocation
- Allocated amounts per subcategory
- Recurring allocation tracking
- Links to budget and subcategory

### Transaction
- Financial transactions
- Amount (positive for income, negative for expenses)
- Category and subcategory links
- Date, description, comments

### Account
- Bank account management
- Current balances
- Account types

### Recurring Models
- Recurring income sources
- Recurring budget allocations
- Auto-population settings

## Development

### Running in Development Mode

1. Ensure you have the development dependencies installed
2. Set `FLASK_ENV=development` and `FLASK_DEBUG=True` in your `.env`
3. Run with `python app.py`
4. The app will auto-reload on code changes

### Database Migrations

When making changes to models:

1. Create a new migration:
   ```bash
   python -m flask db migrate -m "Description of changes"
   ```

2. Apply the migration:
   ```bash
   python -m flask db upgrade
   ```

### Testing

The application includes comprehensive error handling and validation. Test all features thoroughly after making changes.

## Troubleshooting

### Common Issues

**Database errors:**
- Delete `instance/wealthwise.db` and run `python -m flask db upgrade`

**Import errors:**
- Ensure you're in the correct directory
- Check that all dependencies are installed
- Verify virtual environment is activated

**Port already in use:**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Open an issue in the repository
- Check the Help section in the application (`/help`)

## Inspiration

Built with faith and love for Christian families, inspired by the principles of faithful stewardship found in Matthew 25:14-30 and Proverbs 21:5.

---

**Version**: 1.0
**Last Updated**: October 2025