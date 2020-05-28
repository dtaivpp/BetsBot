import boto3
from boto3.dynamodb import Attr
import time
import datetime
import math

dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
bets_table = dynamodb.Table('Daily_Bets')
symbol_outlook_table = dynamodb.Table('Symbol_Outlook')

def lambda_aggregate_outlook(event, context):
    time_window = 300 # Seconds
    start, end = previous_x_seconds(time_window)

    # query db
    results = last_x_seconds_bets(start, end)

    # reduce results
    symbols = {}
    for result in results:
        if (result['sybmol']) not in symbols.keys():
            symbols[result['sybmol']] = {'positive': 0, 'negative': 0}
        
        if result['sentiment'] == True:
            symbols[result['symbol']]['positive'] += 1
        else:
            symbols[result['symbol']]['negative'] += 1
    
    # send to db
    store_results(symbols)


def previous_x_seconds(time_window: int) -> (int, int):
    time_window
    curr_time = math.floor(time.time())
    remainder = curr_time % 300
    
    start_time = curr_time - remainder - 300
    end_time = curr_time - remainder

    return start_time, end_time


def last_x_seconds_bets(start, end) -> list:
    response = bets_table.scan(
            FilterExpression=Attr('updated_utc').between(start, end)
        )
    return response


def store_results(symbols: dict):
    day_val = vote_for_day_utc()
    batch_write = []

    for key, value in symbols:
        try:
            # See if symbol already in table
            response = table.get_item(Key={
                'symbol': key,
                'date': day_val
            })
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            # If there is a item attribute they have
            #   upate the item instead
            if 'Item' in response:
                item = response['Item']
                
                update_item(item, value)

            else:
                batch_write.append({'symbol': key, 
                                    'date': day_val,
                                    'positive': value['positive'],
                                    'negative': value['negative']
                                    })
    
    batch_write_items(batch_write)



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


def update_item(item, value):
    symbol_outlook_table.update_item(
        Key={
            'symbol': key,
            'date': item['date']
        },
        UpdateExpression='SET positive = :pos, negative = :neg',
        ExpressionAttributeVlause={
            ':pos' = value['positive'] + item['positive'],
            ':neg' = value['negative'] + item['negative']
        }
    )


def batch_write_items(items):
    with symbol_outlook_table.batch_write() as batch:
        for item in items:
            batch.put_item(
                Item=item
            )