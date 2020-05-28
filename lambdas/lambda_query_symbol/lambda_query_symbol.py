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
                     user_agent="betsbot by /u/dtaivp",
                     username="dtaivp")




def lambda_query_symbol(event, context):
    comments = event['comments']

    no_votes, votes = process_comments(comments)

    

def process_comments(comments: list) -> (no_votes: list, votes: list):
    day = vote_for_day_utc()
    no_votes = []
    votes = []

    for comment in comments:
        try:
            # Check if user already has voted
            response = table.get_item(Key={
                'symbol': comment['arg_list'][0]
            })
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            # If there is a item attribute they have
            #   upate the item instead
            if 'Item' in response:
                item = response['Item']
                comment['positive'] = item['positive']
                comment['negative'] = item['negative']
                votes.append(comment)

            else:
                no_votes.append(comment)

    return no_votes, votes



def comment_response(no_votes: list, votes: list):
    '''
    Respond to comments
    '''
    for comment in votes:
        reddit_comment = reddit.comment(comment["id"])
        response = ""
        volume = comment['positive'] + comment['negative']

        if positive > negative:
            response += f""

        reddit_comment.reply(response)
    
    for comment in no_votes:
        reddit_comment = reddit.comment(comment["id"])
        reddit_comment.reply("Yeah... no one has voted on that....")


def vote_for_day_utc() -> int:
    """
    Returns the date period the vote is for. 
    Votes made after 9 am count towards next days sentiment
    """
    if(time.localtime().tm_hour <= 9):
        utc_current_datetime = datetime.now(timezone.utc)
        return int(utc_current_datetime.strptime('%Y%m%d'))
    else:
        utc_current_datetime = datetime.now(timezone.utc) + datetime.timedelta(days=1)
        return int(utc_current_datetime.strptime('%Y%m%d'))