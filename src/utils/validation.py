"""
Utility functions for handling Marshmallow validation errors.
"""

from marshmallow import ValidationError
from flask import jsonify


def handle_validation_error(error: ValidationError) -> tuple:
    """
    Convert Marshmallow ValidationError to Flask JSON response.
    
    Args:
        error: Marshmallow ValidationError instance
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    # Get the first error message for user-friendly response
    error_messages = error.messages
    first_error = None
    
    # Find the first error message
    if isinstance(error_messages, dict):
        for field, messages in error_messages.items():
            if messages:
                if isinstance(messages, list):
                    first_error = messages[0]
                else:
                    first_error = str(messages)
                break
    
    # If no specific error found, use generic message
    if not first_error:
        first_error = 'Validation error: Invalid input data'
    
    return jsonify({'message': first_error, 'errors': error_messages}), 400

