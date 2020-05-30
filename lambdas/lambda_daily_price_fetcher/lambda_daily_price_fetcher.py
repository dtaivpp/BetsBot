from os import environ
import requests
import time
import datetime
from boto3.dynamodb import Attr

tiingo_token = environ['tiingo_token']

dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
symbol_outlook_table = dynamodb.Table('Symbol_Outlook')

headers = {
        'Content-Type': 'application/json',
        'Authorization' : f'Token {tiingo_token}'
        }

requestResponse = requests.get("https://api.tiingo.com/api/test/",
                                    headers=headers)

def lambda_daily_price_fetcher(event, context):
    ticker_list = get_daily_tickers()

    pass

def get_daily_tickers():
    date = current_day_utc()
    response = symbol_outlook_table.scan(
            FilterExpression=Attr('date').eq(date)
        )
    symbols = []
    for item in response['Items']:
        for key in item.keys()
            symbols.append(key)

    return symbols


# get stock prices for those tickers

def current_day_utc() -> int:
    """
    Returns the date period to check for
    """
    utc_current_datetime = datetime.now(timezone.utc)
    return int(utc_current_datetime.strptime('%Y%m%d'))