"""
Category utility functions.
"""

from ..extensions import db
from ..models import Category, Subcategory


def create_default_categories(user_id):
    """Create default categories and subcategories for a new user."""
    default_categories = [
        {
            'name': 'Giving',
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
