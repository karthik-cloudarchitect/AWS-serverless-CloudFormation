import json
import logging
from typing import Dict, Any
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

from dynamodb import update_user, validate_user_data, format_success_response, format_error_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda function to update a user
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Get user ID from path parameters
        path_parameters = event.get('pathParameters', {})
        user_id = path_parameters.get('user_id')
        
        if not user_id:
            return format_error_response(400, "User ID is required")
        
        # Parse request body
        if 'body' in event:
            try:
                update_data = json.loads(event['body'])
            except json.JSONDecodeError:
                return format_error_response(400, "Invalid JSON in request body")
        else:
            return format_error_response(400, "Request body is required")
        
        # Validate update data
        validation_errors = validate_user_data(update_data)
        if validation_errors:
            return format_error_response(400, f"Validation errors: {', '.join(validation_errors)}")
        
        # Update user in DynamoDB
        updated_user = update_user(user_id, update_data)
        
        if updated_user:
            return format_success_response({
                'message': 'User updated successfully',
                'user': updated_user
            })
        else:
            return format_error_response(404, "User not found")
        
    except Exception as e:
        logger.error(f"Error in update_user lambda_handler: {str(e)}")
        return format_error_response(500, "Internal server error") 