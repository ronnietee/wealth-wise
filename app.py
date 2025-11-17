"""
Wealth Wise - Main Application Entry Point

This is a lightweight entry point that uses the modular structure.
"""

import os
from src import create_app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'default'))

if __name__ == '__main__':
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    # Run on all interfaces (0.0.0.0) to allow mobile device connections
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
