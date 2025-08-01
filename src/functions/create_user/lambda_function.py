import json
import logging
from typing import Dict, Any
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

from dynamodb import create_user, validate_user_data, format_success_response, format_error_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda function to create a new user
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse request body
        if 'body' in event:
            try:
                user_data = json.loads(event['body'])
            except json.JSONDecodeError:
                return format_error_response(400, "Invalid JSON in request body")
        else:
            return format_error_response(400, "Request body is required")
        
        # Validate user data
        validation_errors = validate_user_data(user_data)
        if validation_errors:
            return format_error_response(400, f"Validation errors: {', '.join(validation_errors)}")
        
        # Create user
        created_user = create_user(user_data)
        
        # Return success response
        return format_success_response({
            'message': 'User created successfully',
            'user': created_user
        })
        
    except Exception as e:
        logger.error(f"Error in create_user lambda_handler: {str(e)}")
        return format_error_response(500, "Internal server error") 