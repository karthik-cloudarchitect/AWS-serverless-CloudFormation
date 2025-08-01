import json
import logging
from typing import Dict, Any
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

from dynamodb import list_users, format_success_response, format_error_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda function to list all users
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Get query parameters
        query_parameters = event.get('queryStringParameters', {}) or {}
        limit = int(query_parameters.get('limit', 100))
        last_evaluated_key = query_parameters.get('last_evaluated_key')
        
        # Validate limit
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1
        
        # List users from DynamoDB
        result = list_users(limit=limit, last_evaluated_key=last_evaluated_key)
        
        return format_success_response({
            'users': result['users'],
            'count': result['count'],
            'next_token': result['next_token']
        })
        
    except Exception as e:
        logger.error(f"Error in list_users lambda_handler: {str(e)}")
        return format_error_response(500, "Internal server error") 