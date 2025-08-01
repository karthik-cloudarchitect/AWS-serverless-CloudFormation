import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from functions.create_user.lambda_function import lambda_handler

class TestCreateUserFunction:
    
    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.aws_request_id = "test-request-id"
        return context
    
    @pytest.fixture
    def mock_dynamodb_functions(self):
        with patch('functions.create_user.lambda_function.create_user') as mock_create, \
             patch('functions.create_user.lambda_function.validate_user_data') as mock_validate, \
             patch('functions.create_user.lambda_function.format_success_response') as mock_success, \
             patch('functions.create_user.lambda_function.format_error_response') as mock_error:
            yield mock_create, mock_validate, mock_success, mock_error
    
    def test_successful_user_creation(self, mock_context, mock_dynamodb_functions):
        """Test successful user creation"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        
        # Mock return values
        mock_validate.return_value = []
        mock_create.return_value = {
            'user_id': 'test-user-id',
            'name': 'John Doe',
            'email': 'john@example.com',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_success.return_value = {
            'statusCode': 200,
            'body': json.dumps({'data': {'message': 'User created successfully'}})
        }
        
        event = {
            'body': json.dumps({
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 30
            })
        }
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 200
        mock_validate.assert_called_once()
        mock_create.assert_called_once()
        mock_success.assert_called_once()
    
    def test_missing_request_body(self, mock_context, mock_dynamodb_functions):
        """Test error handling when request body is missing"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_error.return_value = {
            'statusCode': 400,
            'body': json.dumps({'error': 'Request body is required'})
        }
        
        event = {}
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 400
        mock_error.assert_called_once_with(400, "Request body is required")
    
    def test_invalid_json_body(self, mock_context, mock_dynamodb_functions):
        """Test error handling for invalid JSON"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_error.return_value = {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
        
        event = {
            'body': 'invalid json'
        }
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 400
        mock_error.assert_called_once_with(400, "Invalid JSON in request body")
    
    def test_validation_errors(self, mock_context, mock_dynamodb_functions):
        """Test error handling when validation fails"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_validate.return_value = ["Name is required", "Email is required"]
        mock_error.return_value = {
            'statusCode': 400,
            'body': json.dumps({'error': 'Validation errors: Name is required, Email is required'})
        }
        
        event = {
            'body': json.dumps({
                'age': 30
            })
        }
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 400
        mock_error.assert_called_once_with(400, "Validation errors: Name is required, Email is required")
    
    def test_dynamodb_error(self, mock_context, mock_dynamodb_functions):
        """Test error handling when DynamoDB operation fails"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_validate.return_value = []
        mock_create.side_effect = Exception("DynamoDB Error")
        mock_error.return_value = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
        
        event = {
            'body': json.dumps({
                'name': 'John Doe',
                'email': 'john@example.com'
            })
        }
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 500
        mock_error.assert_called_once_with(500, "Internal server error")
    
    def test_user_creation_with_optional_fields(self, mock_context, mock_dynamodb_functions):
        """Test user creation with optional fields"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_validate.return_value = []
        mock_create.return_value = {
            'user_id': 'test-user-id',
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30,
            'phone': '123-456-7890',
            'address': '123 Main St',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_success.return_value = {
            'statusCode': 200,
            'body': json.dumps({'data': {'message': 'User created successfully'}})
        }
        
        event = {
            'body': json.dumps({
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 30,
                'phone': '123-456-7890',
                'address': '123 Main St'
            })
        }
        
        response = lambda_handler(event, mock_context)
        
        assert response['statusCode'] == 200
        mock_create.assert_called_once()
        call_args = mock_create.call_args[0][0]
        assert call_args['name'] == 'John Doe'
        assert call_args['email'] == 'john@example.com'
        assert call_args['age'] == 30
        assert call_args['phone'] == '123-456-7890'
        assert call_args['address'] == '123 Main St'
    
    def test_cors_headers_in_response(self, mock_context, mock_dynamodb_functions):
        """Test that CORS headers are included in response"""
        mock_create, mock_validate, mock_success, mock_error = mock_dynamodb_functions
        mock_validate.return_value = []
        mock_create.return_value = {
            'user_id': 'test-user-id',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        mock_success.return_value = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'data': {'message': 'User created successfully'}})
        }
        
        event = {
            'body': json.dumps({
                'name': 'John Doe',
                'email': 'john@example.com'
            })
        }
        
        response = lambda_handler(event, mock_context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*' 