from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['APP_NAME'] = 'STEWARD'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wealthwise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    budget_periods = db.relationship('BudgetPeriod', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategories = db.relationship('Subcategory', backref='category', lazy=True, cascade='all, delete-orphan')

class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    comment = db.Column(db.Text)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategory = db.relationship('Subcategory', backref='transactions')

class BudgetPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "January 2024", "Q1 2024", "Custom Budget"
    period_type = db.Column(db.String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly', 'custom'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Only one active budget per user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    budgets = db.relationship('Budget', backref='period', lazy=True, cascade='all, delete-orphan')

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('budget_period.id'), nullable=False)
    total_income = db.Column(db.Float, default=0)
    balance_brought_forward = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('BudgetAllocation', backref='budget', lazy=True, cascade='all, delete-orphan')
    income_sources = db.relationship('IncomeSource', backref='budget', lazy=True, cascade='all, delete-orphan')

class IncomeSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BudgetAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    allocated_amount = db.Column(db.Float, default=0)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    
    # Relationships
    subcategory = db.relationship('Subcategory', backref='allocations')

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/budgets')
def budgets():
    return render_template('budgets.html')

@app.route('/income')
def income():
    return render_template('income.html')

@app.route('/breakdown')
def breakdown():
    return render_template('breakdown.html')

@app.route('/input')
def input_page():
    return render_template('input.html')



@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        currency=data.get('currency', 'USD')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create default categories
    create_default_categories(user.id)
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'currency': user.currency
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    categories = Category.query.filter_by(user_id=current_user.id).all()
    result = []
    
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'subcategories': []
        }
        
        for subcategory in category.subcategories:
            # Get active budget period
            active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
            allocated = 0
            spent = 0
            
            if active_period:
                budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
                if budget:
                    allocation = BudgetAllocation.query.filter_by(
                        budget_id=budget.id, 
                        subcategory_id=subcategory.id
                    ).first()
                    if allocation:
                        allocated = allocation.allocated_amount
                
                # Calculate spent amount for the current period
                spent_transactions = Transaction.query.filter_by(
                    user_id=current_user.id,
                    subcategory_id=subcategory.id
                ).filter(
                    Transaction.transaction_date >= active_period.start_date,
                    Transaction.transaction_date <= active_period.end_date
                ).all()
                
                spent = sum(t.amount for t in spent_transactions)
            
            subcategory_data = {
                'id': subcategory.id,
                'name': subcategory.name,
                'allocated': allocated,
                'spent': spent,
                'balance': allocated - spent
            }
            category_data['subcategories'].append(subcategory_data)
        
        result.append(category_data)
    
    return jsonify(result)

@app.route('/api/categories', methods=['POST'])
@token_required
def create_category(current_user):
    data = request.get_json()
    
    category = Category(
        name=data['name'],
        user_id=current_user.id
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({'message': 'Category created successfully', 'id': category.id}), 201

@app.route('/api/subcategories', methods=['POST'])
@token_required
def create_subcategory(current_user):
    data = request.get_json()
    
    subcategory = Subcategory(
        name=data['name'],
        category_id=data['category_id']
    )
    
    db.session.add(subcategory)
    db.session.commit()
    
    return jsonify({'message': 'Subcategory created successfully', 'id': subcategory.id}), 201

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    data = request.get_json()
    
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    category.name = data['name']
    db.session.commit()
    
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'})

@app.route('/api/subcategories/<int:subcategory_id>', methods=['PUT'])
@token_required
def update_subcategory(current_user, subcategory_id):
    data = request.get_json()
    
    subcategory = Subcategory.query.get(subcategory_id)
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    # Check if user owns the parent category
    category = Category.query.filter_by(id=subcategory.category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    subcategory.name = data['name']
    db.session.commit()
    
    return jsonify({'message': 'Subcategory updated successfully'})

@app.route('/api/subcategories/<int:subcategory_id>', methods=['DELETE'])
@token_required
def delete_subcategory(current_user, subcategory_id):
    subcategory = Subcategory.query.get(subcategory_id)
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    # Check if user owns the parent category
    category = Category.query.filter_by(id=subcategory.category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'message': 'Subcategory not found'}), 404
    
    db.session.delete(subcategory)
    db.session.commit()
    
    return jsonify({'message': 'Subcategory deleted successfully'})

@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transaction(current_user):
    data = request.get_json()
    
    # Get transaction date from request or use current time
    if 'transaction_date' in data:
        transaction_date = datetime.fromisoformat(data['transaction_date'].replace('Z', '+00:00'))
    else:
        transaction_date = datetime.utcnow()
    
    # Get active budget period to validate date range
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if active_period:
        # Convert period dates to datetime for comparison
        period_start = datetime.combine(active_period.start_date, datetime.min.time())
        period_end = datetime.combine(active_period.end_date, datetime.max.time())
        
        # Validate transaction date is within active period
        if transaction_date.date() < active_period.start_date or transaction_date.date() > active_period.end_date:
            return jsonify({
                'error': f'Transaction date must be within the active budget period ({active_period.start_date} to {active_period.end_date})'
            }), 400
    
    transaction = Transaction(
        amount=data['amount'],
        description=data.get('description', ''),
        comment=data.get('comment', ''),
        subcategory_id=data['subcategory_id'],
        user_id=current_user.id,
        transaction_date=transaction_date
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction created successfully', 'id': transaction.id}), 201

# Budget Period Management Endpoints
@app.route('/api/budget-periods', methods=['GET'])
@token_required
def get_budget_periods(current_user):
    try:
        periods = BudgetPeriod.query.filter_by(user_id=current_user.id).order_by(BudgetPeriod.created_at.desc()).all()
        return jsonify([{
            'id': period.id,
            'name': period.name,
            'period_type': period.period_type,
            'start_date': period.start_date.isoformat() if period.start_date else None,
            'end_date': period.end_date.isoformat() if period.end_date else None,
            'is_active': period.is_active,
            'created_at': period.created_at.isoformat() if period.created_at else None
        } for period in periods])
    except Exception as e:
        print(f"Error in get_budget_periods: {str(e)}")
        return jsonify({'error': f'Error loading budget periods: {str(e)}'}), 500

@app.route('/api/budget-periods', methods=['POST'])
@token_required
def create_budget_period(current_user):
    data = request.get_json()
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    # Validate date range
    if start_date >= end_date:
        return jsonify({'error': 'Start date must be before end date'}), 400
    
    # Check for overlapping periods of the same type
    # Allow overlaps between different period types (e.g., monthly and quarterly)
    overlapping_periods = BudgetPeriod.query.filter(
        BudgetPeriod.user_id == current_user.id,
        BudgetPeriod.period_type == data['period_type'],
        BudgetPeriod.start_date <= end_date,
        BudgetPeriod.end_date >= start_date
    ).all()
    
    if overlapping_periods:
        period_names = [p.name for p in overlapping_periods]
        return jsonify({
            'error': f'This {data["period_type"]} period overlaps with existing {data["period_type"]} periods: {", ".join(period_names)}'
        }), 400
    
    # Deactivate current active period of the same type
    BudgetPeriod.query.filter_by(
        user_id=current_user.id, 
        is_active=True,
        period_type=data['period_type']
    ).update({'is_active': False})
    
    # Create new period
    period = BudgetPeriod(
        name=data['name'],
        period_type=data['period_type'],
        start_date=start_date,
        end_date=end_date,
        user_id=current_user.id,
        is_active=True
    )
    db.session.add(period)
    db.session.commit()
    
    # Create budget for this period
    budget = Budget(
        period_id=period.id,
        user_id=current_user.id
    )
    db.session.add(budget)
    db.session.commit()
    
    # Create default categories if this is the first budget
    if not Category.query.filter_by(user_id=current_user.id).first():
        create_default_categories(current_user.id)
    
    return jsonify({
        'id': period.id,
        'name': period.name,
        'period_type': period.period_type,
        'start_date': period.start_date.isoformat(),
        'end_date': period.end_date.isoformat(),
        'is_active': period.is_active,
        'budget_id': budget.id
    }), 201

@app.route('/api/budget-periods/<int:period_id>/activate', methods=['POST'])
@token_required
def activate_budget_period(current_user, period_id):
    # Get the period to activate
    period = BudgetPeriod.query.filter_by(id=period_id, user_id=current_user.id).first()
    if not period:
        return jsonify({'message': 'Budget period not found'}), 404
    
    # Deactivate other active periods of the same type
    BudgetPeriod.query.filter_by(
        user_id=current_user.id, 
        is_active=True,
        period_type=period.period_type
    ).update({'is_active': False})
    
    # Activate selected period
    period.is_active = True
    db.session.commit()
    
    return jsonify({'message': 'Budget period activated successfully'})

@app.route('/api/budget-periods/<int:period_id>', methods=['DELETE'])
@token_required
def delete_budget_period(current_user, period_id):
    # Get the period to delete
    period = BudgetPeriod.query.filter_by(id=period_id, user_id=current_user.id).first()
    if not period:
        return jsonify({'message': 'Budget period not found'}), 404
    
    # Delete all transactions that were created during this budget period
    # Transactions are linked to subcategories, so we need to find all transactions
    # that were created between the period's start and end dates
    transactions_to_delete = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= period.start_date,
        Transaction.transaction_date <= period.end_date
    ).all()
    
    print(f"DEBUG: Deleting {len(transactions_to_delete)} transactions for period {period.name}")
    
    # Delete the transactions
    for transaction in transactions_to_delete:
        db.session.delete(transaction)
    
    # Delete the period (cascade will handle related budgets, allocations, income sources, etc.)
    db.session.delete(period)
    db.session.commit()
    
    return jsonify({'message': 'Budget period and all related data deleted successfully'})

@app.route('/api/budget', methods=['GET'])
@token_required
def get_budget(current_user):
    try:
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not active_period:
            return jsonify({
                'error': 'No active budget period found',
                'message': 'Please create a budget period to begin managing your finances.'
            }), 404
        
        # Get budget for this period
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        
        if not budget:
            return jsonify({
                'error': 'No budget found for active period',
                'message': 'Please create a budget period to begin managing your finances.'
            }), 404
        
        # Calculate total income from income sources
        total_income_from_sources = sum(source.amount for source in budget.income_sources)
        
        return jsonify({
            'budget_id': budget.id,
            'period_id': active_period.id,
            'period_name': active_period.name,
            'period_type': active_period.period_type,
            'start_date': active_period.start_date.isoformat() if active_period.start_date else None,
            'end_date': active_period.end_date.isoformat() if active_period.end_date else None,
            'total_income': total_income_from_sources,
            'balance_brought_forward': budget.balance_brought_forward,
            'balance_to_allocate': total_income_from_sources + budget.balance_brought_forward - sum(a.allocated_amount for a in budget.allocations),
            'income_sources': [{'id': source.id, 'name': source.name, 'amount': source.amount} for source in budget.income_sources]
        })
    except Exception as e:
        print(f"Error in get_budget: {str(e)}")
        return jsonify({'error': f'Error loading budget: {str(e)}'}), 500

@app.route('/api/budget', methods=['PUT'])
@token_required
def update_budget(current_user):
    data = request.get_json()
    
    # Get active budget period
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_period:
        return jsonify({'message': 'No active budget period found'}), 404
    
    budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'message': 'No budget found for active period'}), 404
    
    budget.total_income = data.get('total_income', budget.total_income)
    budget.balance_brought_forward = data.get('balance_brought_forward', budget.balance_brought_forward)
    
    db.session.commit()
    
    return jsonify({'message': 'Budget updated successfully'})

@app.route('/api/allocations', methods=['POST'])
@token_required
def update_allocations(current_user):
    data = request.get_json()
    
    # Get active budget period
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_period:
        return jsonify({'message': 'No active budget period found'}), 404
    
    budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'message': 'No budget found for active period'}), 404
    
    # Calculate total allocation amount
    total_allocation = sum(allocation['amount'] for allocation in data['allocations'])
    available_amount = budget.total_income + budget.balance_brought_forward
    
    # Validate that total allocation doesn't exceed available amount
    if total_allocation > available_amount:
        return jsonify({'message': f'Total allocation (${total_allocation:.2f}) cannot exceed available amount (${available_amount:.2f})'}), 400
    
    # Clear existing allocations
    BudgetAllocation.query.filter_by(budget_id=budget.id).delete()
    
    # Add new allocations
    for allocation in data['allocations']:
        if allocation['amount'] > 0:  # Only add allocations with positive amounts
            new_allocation = BudgetAllocation(
                allocated_amount=allocation['amount'],
                subcategory_id=allocation['subcategory_id'],
                budget_id=budget.id
            )
            db.session.add(new_allocation)
    
    db.session.commit()
    
    return jsonify({'message': 'Allocations updated successfully'})

@app.route('/api/income-sources', methods=['POST'])
@token_required
def create_income_source(current_user):
    try:
        data = request.get_json()
        
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not active_period:
            # Create default monthly period for current month
            current_date = datetime.now()
            start_date = current_date.replace(day=1).date()
            end_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            active_period = BudgetPeriod(
                name=current_date.strftime('%B %Y'),
                period_type='monthly',
                start_date=start_date,
                end_date=end_date,
                user_id=current_user.id,
                is_active=True
            )
            db.session.add(active_period)
            db.session.commit()
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        
        if not budget:
            budget = Budget(
                period_id=active_period.id,
                user_id=current_user.id
            )
            db.session.add(budget)
            db.session.commit()
        
        income_source = IncomeSource(
            name=data['name'],
            amount=data['amount'],
            budget_id=budget.id
        )
        
        db.session.add(income_source)
        db.session.commit()
        
        # Update total income
        budget.total_income = sum(source.amount for source in budget.income_sources)
        db.session.commit()
        
        return jsonify({'message': 'Income source created successfully', 'id': income_source.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating income source: {str(e)}'}), 500

@app.route('/api/income-sources/<int:source_id>', methods=['PUT'])
@token_required
def update_income_source(current_user, source_id):
    data = request.get_json()
    
    # Get active budget period
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_period:
        return jsonify({'message': 'No active budget period found'}), 404
    
    budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
    income_source = IncomeSource.query.filter_by(id=source_id, budget_id=budget.id).first()
    
    if not income_source:
        return jsonify({'message': 'Income source not found'}), 404
    
    income_source.name = data['name']
    income_source.amount = data['amount']
    
    db.session.commit()
    
    # Update total income
    budget.total_income = sum(source.amount for source in budget.income_sources)
    db.session.commit()
    
    return jsonify({'message': 'Income source updated successfully'})

@app.route('/api/income-sources/<int:source_id>', methods=['DELETE'])
@token_required
def delete_income_source(current_user, source_id):
    # Get active budget period
    active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_period:
        return jsonify({'message': 'No active budget period found'}), 404
    
    budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
    income_source = IncomeSource.query.filter_by(id=source_id, budget_id=budget.id).first()
    
    if not income_source:
        return jsonify({'message': 'Income source not found'}), 404
    
    db.session.delete(income_source)
    db.session.commit()
    
    # Update total income
    budget.total_income = sum(source.amount for source in budget.income_sources)
    db.session.commit()
    
    return jsonify({'message': 'Income source deleted successfully'})

@app.route('/api/user/settings', methods=['GET'])
@token_required
def get_user_settings(current_user):
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'currency': current_user.currency
    })

@app.route('/api/user/settings', methods=['PUT'])
@token_required
def update_user_settings(current_user):
    data = request.get_json()
    
    if 'currency' in data:
        current_user.currency = data['currency']
    
    if 'email' in data:
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'message': 'Email already exists'}), 400
        current_user.email = data['email']
    
    db.session.commit()
    
    return jsonify({'message': 'Settings updated successfully'})

@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    
    if not check_password_hash(current_user.password_hash, data['current_password']):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    current_user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    try:
        # Get period type from query parameter (default to 'monthly')
        period_type = request.args.get('period_type', 'monthly')
        
        # Get active budget period of the specified type
        active_period = BudgetPeriod.query.filter_by(
            user_id=current_user.id, 
            is_active=True,
            period_type=period_type
        ).first()
        
        if not active_period:
            return jsonify([])
        
        # Filter transactions by active budget period date range
        transactions = Transaction.query.filter_by(user_id=current_user.id).filter(
            Transaction.transaction_date >= active_period.start_date,
            Transaction.transaction_date <= active_period.end_date
        ).order_by(Transaction.transaction_date.desc()).all()
        
        result = []
        for transaction in transactions:
            subcategory = Subcategory.query.get(transaction.subcategory_id)
            category = Category.query.get(subcategory.category_id) if subcategory else None
            
            result.append({
                'id': transaction.id,
                'amount': transaction.amount,
                'description': transaction.description or '',
                'comment': transaction.comment or '',
                'subcategory_id': transaction.subcategory_id,
                'transaction_date': transaction.transaction_date.isoformat(),
                'category_name': category.name if category else 'Unknown',
                'subcategory_name': subcategory.name if subcategory else 'Unknown'
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_transactions: {str(e)}")
        return jsonify({'error': f'Error loading transactions: {str(e)}'}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(current_user, transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    # Check if transaction_date is being updated
    if 'transaction_date' in data:
        new_transaction_date = datetime.fromisoformat(data['transaction_date'].replace('Z', '+00:00'))
        
        # Get active budget period to validate date range
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if active_period:
            # Validate new transaction date is within active period
            if new_transaction_date.date() < active_period.start_date or new_transaction_date.date() > active_period.end_date:
                return jsonify({
                    'error': f'Transaction date must be within the active budget period ({active_period.start_date} to {active_period.end_date})'
                }), 400
        
        transaction.transaction_date = new_transaction_date
    
    transaction.amount = data.get('amount', transaction.amount)
    transaction.description = data.get('description', transaction.description)
    transaction.comment = data.get('comment', transaction.comment)
    transaction.subcategory_id = data.get('subcategory_id', transaction.subcategory_id)
    
    db.session.commit()
    
    return jsonify({'message': 'Transaction updated successfully'})

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted successfully'})

@app.route('/api/budget/balance-check', methods=['GET'])
@token_required
def check_budget_balance(current_user):
    """Check if total income is sufficient for total allocated budget"""
    try:
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not active_period:
            return jsonify({
                'is_balanced': True,
                'message': 'No active budget period found'
            })
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        
        if not budget:
            return jsonify({
                'is_balanced': True,
                'message': 'No budget found for active period'
            })
        
        # Calculate total income from income sources
        total_income = sum(source.amount for source in budget.income_sources)
        total_income += budget.balance_brought_forward or 0
        
        # Calculate total allocated amount
        total_allocated = sum(allocation.allocated_amount for allocation in budget.allocations)
        
        # Check if budget is balanced
        is_balanced = total_income >= total_allocated
        deficit = total_allocated - total_income if not is_balanced else 0
        
        return jsonify({
            'is_balanced': is_balanced,
            'total_income': total_income,
            'total_allocated': total_allocated,
            'deficit': deficit,
            'message': f'Budget is {"balanced" if is_balanced else "unbalanced"}. {"Deficit: $" + f"{deficit:.2f}" if not is_balanced else ""}'
        })
        
    except Exception as e:
        print(f"Error in check_budget_balance: {str(e)}")
        return jsonify({'error': f'Error checking budget balance: {str(e)}'}), 500

@app.route('/api/budget/overspending-check', methods=['GET'])
@token_required
def check_overspending(current_user):
    """Check for subcategories where spending exceeds allocation"""
    try:
        # Get active budget period
        active_period = BudgetPeriod.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not active_period:
            return jsonify({
                'has_overspending': False,
                'overspent_categories': [],
                'message': 'No active budget period found'
            })
        
        budget = Budget.query.filter_by(period_id=active_period.id, user_id=current_user.id).first()
        
        if not budget:
            return jsonify({
                'has_overspending': False,
                'overspent_categories': [],
                'message': 'No budget found for active period'
            })
        
        overspent_categories = []
        
        # Get all subcategories for the user
        subcategories = Subcategory.query.join(Category).filter(Category.user_id == current_user.id).all()
        print(f"DEBUG: Found {len(subcategories)} subcategories for user {current_user.id}")
        
        for subcategory in subcategories:
            # Get allocation for this subcategory
            allocation = BudgetAllocation.query.filter_by(
                budget_id=budget.id,
                subcategory_id=subcategory.id
            ).first()
            
            allocated_amount = allocation.allocated_amount if allocation else 0
            
            # Calculate spent amount for the current period
            spent_transactions = Transaction.query.filter_by(
                user_id=current_user.id,
                subcategory_id=subcategory.id
            ).filter(
                Transaction.transaction_date >= active_period.start_date,
                Transaction.transaction_date <= active_period.end_date
            ).all()
            
            spent_amount = sum(t.amount for t in spent_transactions)
            
            # Check if overspent
            print(f"DEBUG: {subcategory.name}: allocated={allocated_amount}, spent={spent_amount}")
            if spent_amount > allocated_amount:
                overspent_amount = spent_amount - allocated_amount
                print(f"DEBUG: OVERSHOT! {subcategory.name} by {overspent_amount}")
                
                # Calculate percentage (handle division by zero for 0 allocation)
                if allocated_amount > 0:
                    overspent_percentage = (overspent_amount / allocated_amount) * 100
                else:
                    overspent_percentage = 100  # 100% over when allocation is 0
                
                overspent_categories.append({
                    'subcategory_id': subcategory.id,
                    'subcategory_name': subcategory.name,
                    'category_name': subcategory.category.name,
                    'allocated': allocated_amount,
                    'spent': spent_amount,
                    'overspent_amount': overspent_amount,
                    'overspent_percentage': overspent_percentage
                })
        
        # Sort by overspent amount (highest first)
        overspent_categories.sort(key=lambda x: x['overspent_amount'], reverse=True)
        
        print(f"DEBUG: Final result - {len(overspent_categories)} overspent categories")
        for cat in overspent_categories:
            print(f"DEBUG:   - {cat['category_name']} - {cat['subcategory_name']}: {cat['overspent_amount']} over")
        
        return jsonify({
            'has_overspending': len(overspent_categories) > 0,
            'overspent_categories': overspent_categories,
            'total_overspent_categories': len(overspent_categories),
            'message': f'Found {len(overspent_categories)} overspent subcategor{"y" if len(overspent_categories) == 1 else "ies"}'
        })
        
    except Exception as e:
        print(f"Error in check_overspending: {str(e)}")
        return jsonify({'error': f'Error checking overspending: {str(e)}'}), 500


def create_default_categories(user_id):
    default_categories = [
        {
            'name': 'Church and Family',
            'subcategories': ['Tithe', 'Offering', 'Social Responsibility']
        },
        {
            'name': 'Groceries and Food',
            'subcategories': ['Groceries', 'Dining out']
        },
        {
            'name': 'Home Expenses',
            'subcategories': ['Water bill', 'Electricity bill', 'Fibre', 'Rent/Bond repayment']
        },
        {
            'name': 'Monthly Commitments',
            'subcategories': ['Medical Aid', 'Life cover', 'Netflix', 'Education', 'Phone', 'Banking Fees']
        },
        {
            'name': 'Car and Travel',
            'subcategories': ['Car finance', 'Car insurance', 'Car Tracker', 'Fuel', 'Car wash']
        },
        {
            'name': 'Personal Care',
            'subcategories': []
        },
        {
            'name': 'Leisure',
            'subcategories': []
        },
        {
            'name': 'Other',
            'subcategories': []
        }
    ]
    
    for cat_data in default_categories:
        category = Category(name=cat_data['name'], user_id=user_id)
        db.session.add(category)
        db.session.flush()  # Get the category ID
        
        for subcat_name in cat_data['subcategories']:
            subcategory = Subcategory(name=subcat_name, category_id=category.id)
            db.session.add(subcategory)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)