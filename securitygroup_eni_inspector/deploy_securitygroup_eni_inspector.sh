#!/bin/bash

# Prompt the user for the region name.
read -p "Enter the name of the AWS region: " REGION_NAME

LAMBDA_FUNCTION_NAME="securitygroup-eni-inspector"
LAMBDA_EXECUTION_ROLE="securitygroup-eni-inspector-role"
ACCOUNT_ID="${AWS_ACCOUNT_ID}"

# Error handling function.
handle_error() {
    echo "$1"
    exit 1
}

# Create the Lambda Execution Role.
ROLE_ARN=$(aws iam create-role \
    --role-name "$LAMBDA_EXECUTION_ROLE" \
    --assume-role-policy-document '{
    	"Version": "2012-10-17",
    	"Statement": [
        	{
            	"Effect": "Allow",
            	"Principal": {
                	"Service": "lambda.amazonaws.com"
            	},
            	"Action": "sts:AssumeRole"
        	}
    	]
	}' \
	--query "Role.Arn" \
	--output text) || handle_error "Failed to create Lambda Execution Role."

echo "$ROLE_ARN"

# Attach the AWSLambdaBasicExecutionRole policy to the Lambda Execution Role.
aws iam attach-role-policy \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" \
    --role-name "$LAMBDA_EXECUTION_ROLE" || handle_error "Failed to attach AWSLambdaBasicExecutionRole to Lambda Execution Role."

# Create an IAM Permissions Policy.
POLICY_ARN=$(aws iam create-policy \
    --policy-name "ENISecurityGroupReadOnlyAccess" \
    --policy-document '{
    	"Version": "2012-10-17",
    	"Statement": [
        	{
            	"Sid": "VisualEditor0",
            	"Effect": "Allow",
            	"Action": [
                	"ec2:DescribeNetworkInterfaces",
                	"ec2:DescribeSecurityGroups"
            	],
            	"Resource": "*"
        	}
    	]
	}' \
	--query "Policy.Arn" \
	--output text) || handle_error "Failed to create ENISecurityGroupReadOnlyAccess policy."

echo "ENISecurityGroupReadOnlyAccess policy created successfully."

# Attach the ENISecurityGroupReadOnlyAccess policy to the Lambda Execution Role.
aws iam attach-role-policy \
    --policy-arn "$POLICY_ARN" \
    --role-name "$LAMBDA_EXECUTION_ROLE" || handle_error "Failed to attach ENISecurityGroupReadOnlyAccess to the Lambda Execution Role."

echo "Lambda Execution Role ($LAMBDA_EXECUTION_ROLE) created successfully."

# Zip the Lambda Function code.
zip deployment_package.zip app.py

# Introduce a delay of 30 seconds to allow for IAM Role propagation.
echo "Waiting for IAM Role propagation..."
sleep 30

# Create the Lambda Function.
aws lambda create-function \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --runtime "python3.10" \
    --role "$ROLE_ARN" \
    --handler "app.lambda_handler" \
    --timeout "900" \
    --memory-size "1024" \
    --zip-file fileb://deployment_package.zip \
    --environment Variables="{region_name=$REGION_NAME}" || handle_error "Failed to create Lambda Function."

echo "Lambda Function ($LAMBDA_FUNCTION_NAME) created successfully."