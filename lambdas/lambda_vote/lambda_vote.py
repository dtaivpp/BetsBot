import boto3
import praw
import time
import math

from os import environ
from StockList import stocks

# Get DynamoDB Resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
table = dynamodb.Table('Daily_Bets')

# Authenticate to reddit
reddit = praw.Reddit(client_id=environ["client_id"],
                     client_secret=environ["client_secret"],
                     password=environ["password"],
                     user_agent="Betsbot by /u/dtaivp",
                     username="dtaivp")


class InvalidSentiment(Exception):
    pass


def lambda_vote(event, context):
    '''
    Processes a vote action
    '''
    comments = event['comments']
    process = []
    reject = []

    for comment in comments:
        try:
            comment['sentiment'] = calc_sentiment(comment)
        
            if valid_vote(comment):
                process.append(comment)
            else:
                comment['reject-reason'] = "Invalid Symbol"
                reject.append(comment)

        except InvalidSentiment:
            comment['reject-reason'] = "Invalid Sentiment"
            reject.append(comment)

    batch_write_list, update_list = process_comments(process)

    # send to db
    batch_write(batch_write_list)
    update_sentiment(update_list)

    # send responses
    comment_response(processed, reject)


def process_comments(comments: list) -> (batch_create: list, update: list):
    update_sentiment = []
    batch_write = []

    for comment in comments:
        try:
            # Check if user already has voted
            response = table.get_item(Key={
                'username': f"u/{comment['author']}",
                'symbol': comment['arg_list'][0]
            })
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            # If there is a item attribute they have
            #   upate the item instead
            if 'Item' in response:
                item = response['Item']
                
                ##### TO DO WHAT TO DO IF THEIR VOTE MATCHES PREVIOUS
                if item['bet'] != comment['sentiment']:
                    update_sentiment.append(comment)
                else:
                    pass

            else:
                batch_write.append(comment)

    return batch_write, update_sentiment


def valid_vote(comment):
    '''
    Check if the symbol is in the stock list
    '''
    if comment['arg_list'][0] in stocks:
        return True
    
    return False


def calc_sentiment(comment: dict) -> bool:
    '''
    Determine if comment is positive or negative
    '''
    positive = set(":)", "(:","=)","(=")
    negative = set(":(", "):","=(",")=")

    if comment['arg_list'][1] in positive:
        return True
    
    if comment['arg_list'][1] in negative:
        return False
    
    raise InvalidSentiment()

def batch_write(comments: list):
    '''
    Batch Write new user bets to dynamodb
    '''
    with table.batch_writer() as batch:
        batch.put_item(
            Item={
                "username": f"u/{comment['author']}",
                "symbol": comment['arg_list'][0],
                "bet": comment['sentiment'],
                "created_utc": comment['created_utc'],
                "updated_utc": math.floor(time.time())
                }
            }
        )


def update_sentiment(comments: list):
    '''
    Update bets for existing bets in dynamodb
    '''
    for comment in comments:
        table.update_item(
            Key={
                "username": f"u/{comment['author']}",
                "symbol": comment['arg_list'][0]
            },
            UpdateExpression='SET bet = :val1, updated_utc = :val2',
            ExpressionAttributeValues={
                ':val1': comment['sentiment'],
                ':val2': math.floor(time.time())
            }
        )


def comment_response(processed: list, rejected: list):
    '''
    Respond to comments
    '''
    for comment in rejected:
        reddit_comment = reddit.comment(comment["id"])
        response = ""
        
        if comment['reject-reason'] == "Invalid Sentiment":
            response = """Not even a valid sentiment. Lets keep it simple stupid. Only use :) or :("""

        if comment['reject-reason'] == "Invalid Symbol"
            response = """I dont have that stock symbol. I do NASDAQ, AMEX, or NYSE"""
        
        if response == "":
            response = """Bro I dont even know. Paging u/dtaivp"""

        reddit_comment.reply(response)
    
    for comment in processed:
        reddit_comment = reddit.comment(comment["id"])
        reddit_comment.reply("Yeah I got your vote.")