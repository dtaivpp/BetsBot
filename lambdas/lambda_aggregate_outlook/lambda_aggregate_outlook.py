import boto3
import time
import math

dynamodb = boto3.resource('dynamodb', region_name='us-east-3')
bets_table = dynamodb.Table('Daily_Bets')


def lambda_aggregate_outlook():
    time_window = 300 # Seconds
    start, end = previous_x_min(time_window)

    # query db

    # reduce results

    # send to db


def previous_x_min(time_window: int) -> (int, int):
    time_window
    curr_time = math.floor(time.time())
    remainder = curr_time % 300
    
    start_time = curr_time - remainder - 300
    end_time = curr_time - remainder

    return start_time, end_time
