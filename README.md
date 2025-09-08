# Wealth Wise - Christian Family Budgeting Tool

A beautiful, mobile-friendly budgeting application designed specifically for Christian families to manage their finances with wisdom and faith.

## Features

- **Faith-Based Categories**: Pre-configured with Christian values including tithe, offering, and social responsibility
- **Mobile Responsive**: Works perfectly on all devices
- **Real-time Tracking**: Track spending against allocated budgets with live updates
- **Family Focused**: Designed for Christian families to manage finances together
- **Beautiful UI**: Cozy, modern design with a warm, welcoming feel

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with modern design principles

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wealth-wise
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   - Install PostgreSQL on your system
   - Create a database named `wealthwise`
   - Update the database URL in `config.py` or set the `DATABASE_URL` environment variable

4. **Set up environment variables**
   ```bash
   # Create a .env file with:
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost/wealthwise
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Usage

### Getting Started

1. **Sign Up**: Create a new account with your username, email, and preferred currency
2. **Set Income**: Enter your monthly income and any balance brought forward
3. **Allocate Budget**: Distribute your available funds across different categories
4. **Track Expenses**: Record your daily expenses and see real-time budget updates
5. **Monitor Progress**: Use the summary page to track your financial health

### Default Categories

The application comes with pre-configured categories:

- **Church and Family**: Tithe, Offering, Social Responsibility
- **Groceries and Food**: Groceries, Dining out
- **Home Expenses**: Water bill, Electricity bill, Fibre, Rent/Bond repayment
- **Monthly Commitments**: Medical Aid, Life cover, Netflix, Education, Phone, Banking Fees
- **Car and Travel**: Car finance, Car insurance, Car Tracker, Fuel, Car wash
- **Personal Care**: (Customizable)
- **Leisure**: (Customizable)
- **Other**: (Customizable)

### Key Features

- **Monthly Budget Cycle**: Start your budget cycle whenever you receive your salary
- **Real-time Balance**: See available funds to allocate in real-time
- **Expense Tracking**: Quick expense entry with category and subcategory selection
- **Visual Progress**: Progress bars and color-coded indicators for budget health
- **Mobile Friendly**: Responsive design that works on all screen sizes

## API Endpoints

### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - User login

### Budget Management
- `GET /api/budget` - Get current month's budget
- `PUT /api/budget` - Update income and balance brought forward
- `POST /api/allocations` - Update budget allocations

### Categories
- `GET /api/categories` - Get user's categories with current allocations
- `POST /api/categories` - Create new category
- `POST /api/subcategories` - Create new subcategory

### Transactions
- `POST /api/transactions` - Add new expense transaction

## Database Schema

The application uses the following main tables:

- **users**: User accounts and preferences
- **categories**: Budget categories
- **subcategories**: Budget subcategories
- **transactions**: Expense transactions
- **budgets**: Monthly budget records
- **budget_allocations**: Allocated amounts per subcategory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue in the repository.

## Inspiration

Built with faith and love for Christian families, inspired by Proverbs 21:5: "The plans of the diligent lead to profit as surely as haste leads to poverty."
