from os import environ
import requests
import time
import datetime
from boto3.dynamodb import Attr

tiingo_token = environ['tiingo_token']

dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
symbol_outlook_table = dynamodb.Table('Symbol_Outlook')
symbol_price_table = dynamodb.Table('Symbol_Price')

headers = {
        'Content-Type': 'application/json',
        'Authorization' : f'Token {tiingo_token}'
        }

requestResponse = requests.get("https://api.tiingo.com/api/test/",
                                    headers=headers)

def lambda_daily_price_fetcher(event, context):
    ticker_list = get_daily_tickers()

    price_list = get_stock_prices(ticker_list)

    store_prices(price_list)

    return

def get_daily_tickers():
    date = current_day_utc()
    response = symbol_outlook_table.scan(
            FilterExpression=Attr('date').eq(date)
        )
    symbols = []
    for item in response['Items']:
        for key in item.keys():
            symbols.append(key)

    return symbols


# get stock prices for those tickers
def get_stock_prices(symbols: list) -> list:
    price_list=[]

    for symbol in symbols:
        url = generate_url(symbol)
        response = requests.get(url=url, headers=headers)
        price = response.json()
        price['symbol'] = symbol
        price_list.append(price)


def generate_url(symbol: str) -> str:
    return f"https://api.tiingo.com/tiingo/daily/{symbol}/prices"


def store_prices(prices: list):
    with symbol_outlook_table.batch_write() as batch:
        for price in prices:
            batch.put_item(
                Item=tiingo_serialize(price)
            )


def tiingo_serialize(item):
    return {
        'symbol': item['symbol'],
        'date': current_day_utc(),
        'open': item['open'],
        'close': item['close'],
        'high': item['high'],
        'low': item['low'],
        'volume': item['volume']
    }


def current_day_utc() -> int:
    """
    Returns the date period to check for
    """
    utc_current_datetime = datetime.now(timezone.utc)
    return int(utc_current_datetime.strptime('%Y%m%d'))