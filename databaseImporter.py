import boto3
import json

# Get the service resource.
dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')

tableName = 'info'

def createTable():
    print('Creating table...')
    table = dynamodb.create_table(
        TableName=tableName,
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
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    print('Table %s created!' % tableName)


def updateTable():
    print('Updating table %s' % tableName)
    table = dynamodb.Table(tableName)

    # Open JSON file to get course info data
    with open('courses.json', 'r') as file:
        data = json.load(file)

    # Write courses to DynamoDB
    with table.batch_writer() as batch:
        for course in data['courses']:
            print('Adding %s %s' % (course['subj'], course['num']))
            batch.put_item(Item=course)

# If the table does not exist, create it
if tableName not in client.list_tables()['TableNames']:
    createTable()

updateTable()