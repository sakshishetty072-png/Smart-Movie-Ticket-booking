"""
Setup script to create DynamoDB tables for Movie Magic
Run this script to create the required tables
"""

import boto3
from botocore.exceptions import ClientError

# AWS Configuration
AWS_REGION = 'ap-south-1'

def create_tables():
    """Create DynamoDB tables for Movie Magic"""
    
    # Create DynamoDB client
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
    
    tables = [
        {
            'TableName': 'MovieMagic_Users',
            'KeySchema': [
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'MovieMagic_Bookings',
            'KeySchema': [
                {'AttributeName': 'booking_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'booking_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'MovieMagic_Movies',
            'KeySchema': [
                {'AttributeName': 'movie_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'movie_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table_config in tables:
        table_name = table_config['TableName']
        try:
            dynamodb.create_table(**table_config)
            print(f"Creating table: {table_name}...")
            print(f"✅ Table '{table_name}' created successfully!")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"Table '{table_name}' already exists.")
            else:
                print(f"Error creating table '{table_name}': {e}")
    
    print("\nAll tables created!")

if __name__ == '__main__':
    create_tables()

