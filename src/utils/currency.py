"""
Currency utility functions.
"""

def get_currency_symbol(currency):
    """Get currency symbol for a given currency code."""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'ZAR': 'R', 'CAD': 'C$', 'AUD': 'A$',
        'BWP': 'P', 'ZMW': 'K', 'NGN': '₦', 'KES': 'KSh', 'GHS': '₵', 'UGX': 'USh',
        'TZS': 'TSh', 'ETB': 'Br', 'RWF': 'RF', 'MWK': 'MK', 'BRL': 'R$', 'MXN': '$',
        'PHP': '₱', 'INR': '₹', 'JPY': '¥'
    }
    return symbols.get(currency, '$')
