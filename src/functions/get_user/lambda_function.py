import json
import logging
from typing import Dict, Any
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

from dynamodb import get_user, format_success_response, format_error_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda function to get a user by ID
    
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
        
        # Get user from DynamoDB
        user = get_user(user_id)
        
        if user:
            return format_success_response({
                'user': user
            })
        else:
            return format_error_response(404, "User not found")
        
    except Exception as e:
        logger.error(f"Error in get_user lambda_handler: {str(e)}")
        return format_error_response(500, "Internal server error") 