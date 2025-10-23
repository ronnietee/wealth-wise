"""
Wealth Wise - Main Application Entry Point

This is a lightweight entry point that uses the modular structure.
"""

import os
from src import create_app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=True)
