# Filename: courses.py
# Author: Shawn R Moses
# Date: July 9, 2018
# Current Version: 1.3
# Description: Import the JSON file course information to AWS Dynamodb table "info".

import boto3
import json

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')

# Creates a new table
def __createTable():
    print('Creating table...')
    table = dynamodb.create_table(
        TableName='courses',
        KeySchema=[
            {
                'AttributeName': 'classNum',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'classNum',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='courses')
    print('Table created!')

# Adds courses from JSON
def update():
    # If the table does not exist, create it
    if 'courses' not in client.list_tables()['TableNames']:
        __createTable()

    table = dynamodb.Table('courses')

    with open('courses.json', 'r') as file:
            data = json.load(file)

    # Write courses to DynamoDB
    with table.batch_writer() as batch:
            for course in data['courses']:
                print('Adding %s %s' % (course['subj'], course['num']))
                batch.put_item(Item=course)