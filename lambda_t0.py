import re
import boto3

client = boto3.client('lambda')

valid_symbol = re.compile(r'^ \
 (?<PreXChangeCode>[a-z]{2,4}:(?![a-z\d]+\.))? \
 (?<Stock>[a-z]{1,4}|\d{1,3}(?=\.)|\d{4,}) \
 (?<PostXChangeCode>\.[a-z]{2})? \
 $')


def lambda_t0(comments: list):
    valid_votes = set(":)", ":(", "):", "(:")
    votes = []
    symbol_queries = []
    user_queries = []
    send_help = []

    for comment in comments:
        # sanitizes the word list from comment
        tmp = [word.strip() for word in comment.lower().split(" ")[1:]]
        
        if tmp[0].startswith("u/"):
            user_queries.append(comment)
            continue

        if tmp[1] in valid_votes:
            votes.append(comment)
            continue
    
        if valid_symbol.match(tmp[1]):
            symbol_queries.append(comment)
            continue

        send_help.append(comment)
        
        
    disptach_lambda(votes, 'lambda_vote')
    disptach_lambda(symbol_queries, 'lambda_symbol')
    disptach_lambda(user_queries, 'lambda_user_accuracy')
    disptach_lambda(send_help, 'lambda_send_help')


def disptach_lambda(comment_list, target):
    client.invoke(
            FunctionName=target,
            InvocationType='Event',
            LogType='None',
            ClientContext='string',
            Payload={comment_list},
    )

