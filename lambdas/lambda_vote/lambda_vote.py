import boto3
from StockList import stocks

dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
table = dynamodb.Table('daily_bets_table')

def lambda_vote(event, context):
    comments = event['comments']
    
    for comment in comments:

    # send to db

    # send responses

def load_symbols():

    