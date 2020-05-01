import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

users_bets_table = dynamodb.create_table(
    TableName='Users_Bets',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'  #Partition key
        }
        {
            'AttributeName': 'symbol',
            'KeyType': 'range'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'correct',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'incorrect',
            'AttributeType': 'N'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

daily_bets_table = dynamodb.create_table(
    TableName='Daily_Bets',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'  #Partition key
        }
        {
            'AttributeName': 'symbol',
            'KeyType': 'range'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'bet',
            'AttributeType': 'b'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

users_table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'  #Partition key
        }
        {
            'AttributeName': 'source',
            'KeyType': 'range'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'correct',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'incorrect',
            'AttributeType': 'N'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

symbol_outlook_table = dynamodb.create_table(
    TableName='Symbol_Outlook',
    KeySchema=[
        {
            'AttributeName': 'symbol',
            'KeyType': 'HASH'  #Partition key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'outlook',
            'AttributeType': 'b'
        },


    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)