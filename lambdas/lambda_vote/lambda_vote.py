import boto3
from StockList import stocks


dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
table = dynamodb.Table('Daily_Bets')


class InvalidSentiment(Exception):
    pass


def lambda_vote(event, context):
    comments = event['comments']
    process = []
    reject = []

    for comment in comments:
        try:
            comment['sentiment'] = calc_sentiment(comment)
        
            if valid_vote(comment):
                process.append(comment)
            else:
                reject.append(comment)

        except InvalidSentiment:
            reject.append(comment)

    batch_write, update = process_comments(process)

    # send to db


    # send responses


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
    # Check if the symbol is in the stock list
    if comment['arg_list'][0] in stocks:
        return True
    
    return False


def calc_sentiment(comment: dict) -> bool:
    positive = set(":)", "(:","=)","(=")
    negative = set(":(", "):","=(",")=")

    if comment['arg_list'][1] in positive:
        return True
    
    if comment['arg_list'][1] in negative:
        return False
    
    raise InvalidSentiment()

def batch_write(comments: list):
    with table.batch_writer() as batch:
        batch.put_item(
            Item={
                "username": f"u/{comment['author']}",
                "symbol": comment['arg_list'][0],
                "bet": comment['sentiment']
                }
            }
        )
    
    pass

def update_sentiment(comments: list):
    pass