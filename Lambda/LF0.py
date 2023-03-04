# import boto3
# import json



# def lambda_handler(event, context):
    
#     # client = boto3.client('lex-runtime')
  
#     # lastUserMessage = event["properties"]["messages"]["type"]
#     # botMessage = "Something went wrong!! Please try again"
    
#     # if lastUserMessage is None or len(lastUserMessage) < 1:
#     #     return {
#     #         'statusCode': 200,
#     #         'body': json.dumps(botMessage)
#     #     }
    
#     # # lastUserMessage = lastUserMessage[0]['unstructured']['text']
#     # # Update the user id, so it is different for different user
#     # response = client.post_text(
#     #     botId='OZMYLMR5PP',
#     #     botAliasId='TSTALIASID',
#     #     localeId='en_US',
#     #     sessionId="681054552070211",
#     #     text='bookhotel')
        
#     # # response = client.post_text(botName='booktrip',
#     # #     botAlias='TestBotAlias',
#     # #     userId='testuser',
#     # #     inputText=lastUserMessage)
    
#     # if response['message'] is not None or len(response['message']) > 0:
#     #     botMessage = response['message']
    
#     # print("Bot message", botMessage)
    
#     # botResponse =  [{
#     #     'type': 'unstructured',
#     #     'unstructured': {
#     #       'text': botMessage
#     #     }
#     #   }]
      
#     test = event["properties"]["messages"]["type"]

#     return {
#       "type" : "object",
#         "messages" : [{
#           "type" : 'unstructured',
#           "unstructured": {
#               "type": 'product', 
#               "text" :test + "This works"
#             }
#         }]
#     }

#     return {
#         'statusCode': 200,
#         'messages': botResponse
#     }



import json
import boto3
from botocore.config import Config
import uuid

def lambda_handler(event, context):
    test = event["properties"]["messages"]["type"]
    print(event)
    my_config = Config(
    region_name = 'us-east-1',
    )
    client = boto3.client('lex-runtime',config=my_config)
    # sending request to lex
    response = client.post_text(
    botName='yelpbot',
    botAlias = 'prod',
    #userId=event.messages[0].["unstructured"].["id"],
    # userId=uuid.uuid4().hex,
    userId = '359',
    # userId = event["properties"]["messages"]["id"],
    inputText=test
    # inputText='suggest'
    )
    
#     print(response)
    
    
#     return {
#       "type" : "object",
#         "messages" : [{
#           "type" : 'unstructured',
#           "unstructured": {
#               "type": 'product', 
#               "text" : response['message']
#             #   "text" :test + "This works"
#             }
#         }]
#     }
    # print(response)
    # print(response['ResponseMetadata']['HTTPStatusCode'])
    
    # the response to user from lex
    # we check the response status, messages from response
    # if response['ResponseMetadata']['HTTPStatusCode'] == 200 :
    return {
        "type" : "object",
        "messages" : [{
          "type" : 'unstructured',
          "unstructured": {
              "type": 'product', 
            "text" : response['message']
            #   "text" : event["properties"]["messages"]["type"]
            }
        }]
    }
        # return {
        # 'statusCode': 200,
        # 'headers': {
        #     'Access-Control-Allow-Origin': '*'
        # },
        # "messages": [
        #     {
        #     "type": "unstructured",
        #     "unstructured": {
        #         "id": "string",
        #         "text": response,
        #         "timestamp": "string"
        #         }
        #     }
        # ]
        # }
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


# import json
# import boto3
# import logging
# from botocore.config import Config

# def lambda_handler(event, context):
    
#     # return {
#     #     'statusCode': 200,
#     #     'body': event['messages'][0]['unstructured']['text'],
#     #     "headers": { 
#     #         "Access-Control-Allow-Origin": "*" 
#     #     }
#     # }
  
#     my_config = Config(
#     region_name = 'us-east-1',
#     )
#     client = boto3.client('lex-runtime',config=my_config)
#     # client = boto3.client('lex-runtime')
    
#     response = client.post_text(
#         botName='yelpbot',
#         botAlias='prod',
#         userId='lf0',
#         inputText='Hi')
#         # inputText=event['messages'][0]['unstructured']['text'])
        
#     return {
#         'statusCode': 200,
#         'body': response,
#         "headers": { 
#             "Access-Control-Allow-Origin": "*" 
#         }
#     }