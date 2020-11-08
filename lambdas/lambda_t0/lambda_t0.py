import re
import requests
import time
import datetime as dt
import boto3

client = boto3.client('lambda')

symbol_pattern =r'^(?P<PreXChangeCode>[a-z]{2,4}:(?![a-z\d]+\.))?(?P<Stock>[a-z]{1,4}|\d{1,3}(?=\.)|\d{4,})(?P<PostXChangeCode>\.[a-z]{2})?$'

def lambda_t0(event, context):
    '''
    Comment Collection and Catagorization
    '''

    # Used for testing outside aws
    if context != None:
        comments = get_comments(uri)
    else:
        comments = sample_comments()

    # Set of valid vote options
    valid_votes = set({":(", "):", "=(", ")=", ":)", "(:","=)","(="})
    votes = []
    symbol_queries = []
    user_queries = []
    send_help = []


    for comment in comments:
        # Cleans comment for processing
        tmp = [word.strip() for word in comment['body'].lower().split(" ")[1:]]
        
        # todo: extract comment to own class
        comment['arg_list'] = tmp

        # Catagorize 
        if tmp[0].startswith("u/"):
            user_queries.append(comment)
            continue

        if re.match(symbol_pattern, tmp[0]) and len(tmp) == 1:
            symbol_queries.append(comment)
            continue

        if len(tmp) > 1 and tmp[1] in valid_votes:
            votes.append(comment)
            continue

        # if it matches nothing I didnt get it
        send_help.append(comment)
    
    # Send each list to respective lambdas for processing
    if len(votes) > 0:
        disptach_lambda(votes, 'lambda_vote')
    
    if len(symbol_queries) > 0:
        disptach_lambda(symbol_queries, 'lambda_symbol')
    
    if len(user_queries) > 0:
        disptach_lambda(user_queries, 'lambda_user_accuracy')
    
    if len(send_help) > 0:
        disptach_lambda(send_help, 'lambda_send_help')


def disptach_lambda(comment_list, target):
    '''
    Abstraction for dispatching lambda via boto
    '''
    #[print(comment['author', target]) for comment in comment_list]
    client.invoke(
            FunctionName=target,
            InvocationType='Event',
            LogType='None',
            ClientContext='string',
            Payload={comment_list},
    )

def last_min_epoch_time():
    '''Returns the start and end of
    the last minute in epoch time'''
    currDate = dt.datetime.now()
    currDate.replace(second = 0)
    currDate.replace(microsecond = 0)
    currDate -= dt.timedelta(minutes=1)
    endtime = currDate
    endtime.replace(second = 59)
    endtime.replace(microsecond = 999)
    
    return int(currDate.timestamp()), int(endtime.timestamp())


def get_comments(uri: str):
    '''
    Get Comments from PushShift
    '''
    after, before = last_min_epoch_time()
    uri += f'&after={after}&before={before}'
    
    response = requests.get(
        uri
    )

    if response.status_code != 200:
        raise Exception(f"Response with invalid status code: {response.status_code}")

    data = response.json()

    return data['data']


if __name__=='__main__':
    lambda_t0('https://api.pushshift.io/reddit/comment/search?subreddit=wallstreetbets&q=!BetsBot')
