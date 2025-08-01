# Serverless Architecture: API Gateway → Lambda → DynamoDB (CloudFormation)

This repository contains the CloudFormation implementation of a serverless architecture using AWS services.

## Architecture Overview

```
Client → API Gateway → Lambda → DynamoDB
```

## Components

- **API Gateway**: Receives HTTP requests and routes to Lambda functions
- **Lambda Functions**: Process requests and interact with DynamoDB
- **DynamoDB**: NoSQL database for data storage
- **IAM Roles & Policies**: Security and permissions

## Prerequisites

- AWS CLI configured
- Python 3.8+
- AWS SAM CLI (for local testing)

## Project Structure

```
serverless-cf/
├── README.md
├── requirements.txt
├── template.yaml
├── src/
│   ├── utils/
│   │   └── dynamodb.py
│   └── functions/
│       ├── create_user/
│       │   └── lambda_function.py
│       ├── get_user/
│       │   └── lambda_function.py
│       ├── list_users/
│       │   └── lambda_function.py
│       ├── update_user/
│       │   └── lambda_function.py
│       └── delete_user/
│           └── lambda_function.py
└── tests/
    └── test_create_user.py
```

## Deployment

### Using AWS CLI

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build SAM application:
   ```bash
   sam build
   ```

3. Deploy the stack:
   ```bash
   sam deploy --guided
   ```

### Using CloudFormation Console

1. Upload the `template.yaml` file to CloudFormation console
2. Create stack with the template
3. Provide required parameters

## Testing

Run the tests:
```bash
pytest tests/
```

## Features

- Complete CRUD operations for users
- DynamoDB integration with proper error handling
- API Gateway with CORS support
- Comprehensive input validation
- Detailed logging and monitoring

## Cleanup

```bash
sam delete --stack-name serverless-architecture
```

## API Endpoints

- `POST /users` - Create a new user
- `GET /users` - List all users (with pagination)
- `GET /users/{user_id}` - Get a specific user
- `PUT /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

## Monitoring

- CloudWatch Logs for Lambda functions
- DynamoDB metrics and alarms
- API Gateway access logs
- X-Ray tracing (optional) 