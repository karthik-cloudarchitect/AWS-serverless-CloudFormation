import boto3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')

def get_table():
    """Get DynamoDB table instance"""
    return dynamodb.Table(table_name)

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user in DynamoDB
    
    Args:
        user_data: User data dictionary
        
    Returns:
        Created user data
    """
    try:
        table = get_table()
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Prepare item
        item = {
            'user_id': user_id,
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add optional fields
        if 'age' in user_data:
            item['age'] = user_data['age']
        if 'phone' in user_data:
            item['phone'] = user_data['phone']
        if 'address' in user_data:
            item['address'] = user_data['address']
        
        # Put item in DynamoDB
        table.put_item(Item=item)
        
        logger.info(f"Created user: {user_id}")
        return item
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise e

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID from DynamoDB
    
    Args:
        user_id: User ID
        
    Returns:
        User data or None if not found
    """
    try:
        table = get_table()
        
        response = table.get_item(
            Key={'user_id': user_id}
        )
        
        if 'Item' in response:
            logger.info(f"Retrieved user: {user_id}")
            return response['Item']
        else:
            logger.info(f"User not found: {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise e

def list_users(limit: int = 100, last_evaluated_key: Optional[str] = None) -> Dict[str, Any]:
    """
    List all users from DynamoDB
    
    Args:
        limit: Maximum number of items to return
        last_evaluated_key: Pagination token
        
    Returns:
        Dictionary with users and pagination info
    """
    try:
        table = get_table()
        
        scan_kwargs = {
            'Limit': limit
        }
        
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = {'user_id': last_evaluated_key}
        
        response = table.scan(**scan_kwargs)
        
        users = response.get('Items', [])
        next_token = response.get('LastEvaluatedKey', {}).get('user_id') if 'LastEvaluatedKey' in response else None
        
        logger.info(f"Retrieved {len(users)} users")
        
        return {
            'users': users,
            'count': len(users),
            'next_token': next_token
        }
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise e

def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a user in DynamoDB
    
    Args:
        user_id: User ID
        update_data: Data to update
        
    Returns:
        Updated user data or None if not found
    """
    try:
        table = get_table()
        
        # Build update expression
        update_expression = "SET updated_at = :updated_at"
        expression_attribute_values = {
            ':updated_at': datetime.utcnow().isoformat()
        }
        
        # Add fields to update
        for key, value in update_data.items():
            if key in ['name', 'email', 'age', 'phone', 'address']:
                update_expression += f", {key} = :{key}"
                expression_attribute_values[f':{key}'] = value
        
        # Update item
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        if 'Attributes' in response:
            logger.info(f"Updated user: {user_id}")
            return response['Attributes']
        else:
            logger.info(f"User not found for update: {user_id}")
            return None
            
    except table.meta.client.exceptions.ResourceNotFoundException:
        logger.info(f"User not found for update: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise e

def delete_user(user_id: str) -> bool:
    """
    Delete a user from DynamoDB
    
    Args:
        user_id: User ID
        
    Returns:
        True if deleted, False if not found
    """
    try:
        table = get_table()
        
        response = table.delete_item(
            Key={'user_id': user_id},
            ReturnValues='ALL_OLD'
        )
        
        if 'Attributes' in response:
            logger.info(f"Deleted user: {user_id}")
            return True
        else:
            logger.info(f"User not found for deletion: {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise e

def validate_user_data(user_data: Dict[str, Any]) -> List[str]:
    """
    Validate user data
    
    Args:
        user_data: User data to validate
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    if not user_data.get('name'):
        errors.append("Name is required")
    
    if not user_data.get('email'):
        errors.append("Email is required")
    elif '@' not in user_data.get('email', ''):
        errors.append("Email must be valid")
    
    # Optional field validation
    if 'age' in user_data:
        try:
            age = int(user_data['age'])
            if age < 0 or age > 150:
                errors.append("Age must be between 0 and 150")
        except (ValueError, TypeError):
            errors.append("Age must be a number")
    
    if 'phone' in user_data and user_data['phone']:
        phone = str(user_data['phone']).replace('-', '').replace(' ', '')
        if not phone.isdigit() or len(phone) < 10:
            errors.append("Phone number must be valid")
    
    return errors

def format_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format API Gateway response
    
    Args:
        status_code: HTTP status code
        body: Response body
        
    Returns:
        Formatted response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': body
    }

def format_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Format error response
    
    Args:
        status_code: HTTP status code
        message: Error message
        
    Returns:
        Formatted error response
    """
    return format_response(status_code, {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    })

def format_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format success response
    
    Args:
        data: Response data
        
    Returns:
        Formatted success response
    """
    return format_response(200, {
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }) 