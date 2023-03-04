# """
# This sample demonstrates an implementation of the Lex Code Hook Interface
# in order to serve Dining Concierge chatbot which manages restaurant reservations.
# Bot, Intent, and Slot models which are compatible with this function can be found in the Lex Console
# as part of the 'DiningConcierge' Bot.

# """
# import math
# import dateutil.parser
# import datetime
# import time
# import os
# import logging
# import boto3

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)


# """ --- Helpers to build responses which match the structure of the necessary dialog actions --- """


# def get_slots(intent_request):
#     return intent_request['currentIntent']['slots']


# def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
#     return {
#         'sessionAttributes': session_attributes,
#         'dialogAction': {
#             'type': 'ElicitSlot',
#             'intentName': intent_name,
#             'slots': slots,
#             'slotToElicit': slot_to_elicit,
#             'message': message
#         }
#     }


# def close(session_attributes, fulfillment_state, message):
#     response = {
#         'sessionAttributes': session_attributes,
#         'dialogAction': {
#             'type': 'Close',
#             'fulfillmentState': fulfillment_state,
#             'message': message
#         }
#     }

#     return response


# def delegate(session_attributes, slots):
#     return {
#         'sessionAttributes': session_attributes,
#         'dialogAction': {
#             'type': 'Delegate',
#             'slots': slots
#         }
#     }


# """ --- Helper Functions --- """


# def parse_int(n):
#     try:
#         return int(n)
#     except ValueError:
#         return float('nan')


# def build_validation_result(is_valid, violated_slot, message_content):
#     if message_content is None:
#         return {
#             "isValid": is_valid,
#             "violatedSlot": violated_slot,
#         }

#     return {
#         'isValid': is_valid,
#         'violatedSlot': violated_slot,
#         'message': {'contentType': 'PlainText', 'content': message_content}
#     }


# def isvalid_date(date):
#     try:
#         dateutil.parser.parse(date)
#         return True
#     except ValueError:
#         return False


# def validate_slot(intent_request):
#     city = intent_request["City"]
#     cuisine_type = intent_request["CuisineType"]
#     date = intent_request["ReservationDate"]
#     reservation_time = intent_request["ReservationTime"]
#     numberOfPeople = intent_request["NumberOfPeople"]

#     cuisine_types = ['indian', 'chinese', 'thai', 'mexican', 'korean']
#     valid_cities = ['new york', 'nyc', 'new york city', 'ny', 'manhattan', 'brooklyn', 'queens', 'staten island']

#     if city is not None and city.lower() not in valid_cities:
#         return build_validation_result(False,
#                                       'City',
#                                       'We do not currently support {}, would you like to choose a locality in New York ? '
#                                       .format(city))

#     if cuisine_type is not None and cuisine_type.lower() not in cuisine_types:
#         return build_validation_result(False,
#                                       'CuisineType',
#                                       'We do not currently support {}, would you like to choose from either Indian, Chinese, Thai, Mexican or  ? '
#                                       .format(cuisine_type, cuisine_types))
    
#     if date is not None:
#         if not isvalid_date(date):
#             return build_validation_result(False, 'ReservationDate', 'I did not understand that, what date would you like to make the reservation?')
#         elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
#             return build_validation_result(False, 'ReservationDate', 'You can only reserve a table from today onwards.  What day would you like to make the reservation?')
    

#     if reservation_time is not None:
#         if len(reservation_time) != 5:
#             # Not a valid time; use a prompt defined on the build-time model.
#             return build_validation_result(False, 'ReservationTime', None)

#         hour, minute = reservation_time.split(':')
#         hour = parse_int(hour)
#         minute = parse_int(minute)
#         if math.isnan(hour) or math.isnan(minute):
#             # Not a valid time; use a prompt defined on the build-time model.
#             return build_validation_result(False, 'ReservationTime', None)

#         if hour < 0 or hour > 24:
#             # Outside of business hours
#             return build_validation_result(False, 'ReservationTime', 'I am sorry that is not a valid time, please enter a valid time.')

   
#     if numberOfPeople is not None and (int(numberOfPeople) < 1):
#         #Less than 1 person
#         return build_validation_result(False, 'NumberOfPeople', 'The minimum number of people is 1. How many people do you have?')
#     #elif math.isnan(numberOfPeople):
#         #return build_validation_result(False, 'NumberOfPeople', 'The minimum number of people is 1. How many people do you have?')

#     return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


# def make_reservation(intent_request):
#     """
#     Performs dialog management and fulfillment for making reservations.
#     Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
#     in slot validation and re-prompting.
#     """

#     city = get_slots(intent_request)["Location"]
#     cuisine_type = get_slots(intent_request)["Cuisine"]
#     date = get_slots(intent_request)["DiningDate"]
#     reservation_time = get_slots(intent_request)["DiningTime"]
#     numberOfPeople = get_slots(intent_request)["NumberOfPeople"]
#     phone = get_slots(intent_request)["Email"]
#     source = intent_request['invocationSource']

#     if source == 'DialogCodeHook':
#         # Perform basic validation on the supplied input slots.
#         # Use the elicitSlot dialog action to re-prompt for the first violation detected.
#         slots = get_slots(intent_request)

#         validation_result = validate_slot(intent_request['currentIntent']['slots'])
#         if not validation_result['isValid']:
#             slots[validation_result['violatedSlot']] = None
#             return elicit_slot(intent_request['sessionAttributes'],
#                               intent_request['currentIntent']['name'],
#                               slots,
#                               validation_result['violatedSlot'],
#                               validation_result['message'])

#         return delegate(intent_request['sessionAttributes'], get_slots(intent_request))
    
#     elif source == 'FulfillmentCodeHook':
#         sqs = boto3.client('sqs', aws_access_key_id="AKIAZWSA32HVFRCEY5F4", aws_secret_access_key="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")
#         response = sqs.get_queue_url(QueueName='DiningChatbot')
#         queue_url = response['QueueUrl']
#         response = sqs.send_message(
#             QueueUrl=queue_url,
#             MessageAttributes={
#                 'Location': {
#                 'DataType': 'String',
#                 'StringValue': city
#                 },
#                 'Cuisine': {
#                 'DataType': 'String',
#                 'StringValue': cuisine_type
#                 },
#                 'reservation_date': {
#                 'DataType': 'String',
#                 'StringValue': date
#                 },
#                 'reservation_time': {
#                 'DataType': 'String',
#                 'StringValue': reservation_time
#                 },
#                 'numberOfPeople': {
#                 'DataType': 'Number',
#                 'StringValue': str(numberOfPeople)
#                 },
#                 'PhoneNumber': {
#                 'DataType': 'String',
#                 'StringValue': str(phone)
#                 }
#             },
#             MessageBody=(
#                 'Customer details for restaurant reservation'
#             )
#         )

#         print('The message id for the response msg is {}'.format(response['MessageId']))
        
#         return close(intent_request['sessionAttributes'],
#                  'Fulfilled',
#                  {'contentType': 'PlainText',
#                   'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'})

# def thank_you(intent_request):
#     # Final goodbye message to the end user
#     return close(intent_request['sessionAttributes'],
#                  'Fulfilled',
#                  {'contentType': 'PlainText',
#                   'content': 'You are welcome'})

# def greetings(intent_request):
#     #Provide greeting to the user
#     return close(intent_request['sessionAttributes'],
#                  'Fulfilled',
#                  {'contentType': 'PlainText',
#                   'content': 'Hello, how can I help you?'})



# """ --- Intents --- """


# def dispatch(intent_request):
#     """
#     Called when the user specifies an intent for this bot.
#     """

#     logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

#     intent_name = intent_request['currentIntent']['name']

#     # Dispatch to your bot's intent handlers
#     if intent_name == 'GreetingIntent':
#         return greetings(intent_request)
#     elif intent_name == 'DiningSuggestionIntent':
#         return make_reservation(intent_request)
#     elif intent_name == 'ThankYouIntent':
#         return thank_you(intent_request)


#     raise Exception('Intent with name ' + intent_name + ' not supported')


# """ --- Main handler --- """


# def lambda_handler(event, context):
#     """
#     Route the incoming request based on intent.
#     The JSON body of the request is provided in the event slot.
#     """
#     # By default, treat the user request as coming from the America/New_York time zone.
#     os.environ['TZ'] = 'America/New_York'
#     time.tzset()
#     logger.debug('event.bot.name={}'.format(event['bot']['name']))

#     return dispatch(event)
import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---

# def sendMsg(slots):
#     # Send message to SQS queue
#     sqs = boto3.client('sqs')
#     queue_url = 'https://sqs.us-east-1.amazonaws.com/681054552070/yelpbot'
#     Attributes={
#         'NoOfPeople': {
#             'DataType': 'String',
#             'StringValue': slots["NumberOfPeople"]
#         },
#         'Date': {
#             'DataType': 'String',
#             'StringValue': slots["DiningDate"]
#         },
#         'Time': {
#             'DataType': 'String',
#             'StringValue': slots["DiningTime"]
#         },
#         'phone' : {
#             'DataType': 'String',
#             'StringValue': slots["phone"]
#         },
#         'Cuisine': {
#             'DataType': 'String',
#             'StringValue': slots["Cuisine"]
#         }
#     }
#     response = sqs.send_message(
#         QueueUrl=queue_url,
#         MessageAttributes=Attributes,
#         MessageBody=('Testing queue')
#         )
#     print(response['MessageId'])

def sendMsg():
    # Send message to SQS queue
    sqs = boto3.client('sqs', aws_access_key_id="AKIA4J6KABAGXUV6X5E3", aws_secret_access_key="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",region_name = 'us-east-1')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/845995313165/chatq'
    Attributes={
        'NoOfPeople': {
            'DataType': 'String',
            'StringValue': "2"
        },
        'Date': {
            'DataType': 'String',
            'StringValue': "2023-03-03"
        },
        'Time': {
            'DataType': 'String',
            'StringValue': "20:00"
        },
        'phone' : {
            'DataType': 'String',
            'StringValue': "9995568"
        },
        'Cuisine': {
            'DataType': 'String',
            'StringValue': "korean"
        }
    }
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes=Attributes,
        MessageBody=('Testing queue')
        )
        
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': 'Message sent'}
        }
    }
    print(response['MessageId'])


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

##########################################################################################################################
# 1. GreetingIntents
# 2. ThankYouIntent
# 3. DiningSuggestionsIntent
# 4. Build validation result
# 5. Validation methods for:
#       a. Cuisine
#       b. Number of people
#       c. date
#       d. time
#       e. city ???

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_cuisine(cuisine):
    cuisines = ['indian', 'thai', 'mediterranean', 'chinese', 'italian']
    return cuisine.lower() in cuisines

def isvalid_numberofpeople(numPeople):
    numPeople = safe_int(numPeople)
    if numPeople > 20 or numPeople < 0:
        return False
    else: 
        return True 
        
def isvalid_date(diningdate):
    # return (isvalid_time(diningtime)['isValid'])
    # if datetime.datetime.strptime(diningdate, '%Y-%m-%d').date() <= datetime.date.today():
        return True
    # else:
    #     return True 
    # return False

def isvalid_time(diningdate, diningtime):
    # if datetime.datetime.strptime(diningdate, '%Y-%m-%d').date() == datetime.date.today():
        # if datetime.datetime.strptime(diningtime, '%H:%M').time() <= datetime.datetime.now().time():
    return True

def validate_dining_suggestion(cuisine, numPeople, diningdate, diningtime):
    if cuisine is not None:
        if not isvalid_cuisine(cuisine):
            return build_validation_result(False, 'Cuisine', 'Cuisine not available. Please try another.')
    
    # if numberPeople is not None and not numberPeople.isnumeric():
    #     return build_validation_result(False,
    #                                   'NumberOfPeople',
    #                                   'That does not look like a valid number {}, '
    #                                   'Could you please repeat?'.format(numberOfPeople))

    if numPeople is not None:
        if not numPeople.isnumeric():
            # return {
            #     'message': {'contentType': 'PlainText', 'content': numPeople}
            # }
            return build_validation_result(False, 'NumberOfPeople', numPeople)
            
    if diningdate is not None:
        if not isvalid_date(diningdate):
            return build_validation_result(False, 'diningdate', 'Please enter valid date')
    
    if diningtime is not None and diningdate is not None:
        if not isvalid_time(diningdate, diningtime):
            return build_validation_result(False, 'diningtime', 'Please enter valid time')

            
            

    return build_validation_result(True, None, None)





def greetings(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': 'Hi there, how can I help you, kishore moorthy?'}
        }
    }

def thank_you(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': 'You are welcome!'}
        }
    }

def dining_suggestions(intent_request):
    slots = intent_request['currentIntent']['slots']
    cuisine = slots["Cuisine"]
    numPeople = slots["NumberOfPeople"]
    diningdate = slots["DiningDate"]
    diningtime = slots["DiningTime"]
    location = slots["Location"]
    phone = slots["phone"]
    
    # return(intent_request['sessionAttributes'])
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_dining_suggestion(cuisine, numPeople, diningdate, diningtime)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                              intent_request['currentIntent']['name'],
                              slots,
                              validation_result['violatedSlot'],
                              validation_result['message'])
    
        if intent_request['sessionAttributes'] is not None:
                output_session_attributes = intent_request['sessionAttributes']
        else:
            output_session_attributes = {}
    
        return delegate(output_session_attributes, intent_request['currentIntent']['slots'])
        
        #         return delegate(intent_request['sessionAttributes'], get_slots(intent_request))
    
    # elif source == 'FulfillmentCodeHook':
    #     sqs = boto3.client('sqs', aws_access_key_id="AKIAZ5EQDYADJ4RSVRWD", aws_secret_access_key="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")
    #     response = sqs.get_queue_url(QueueName='yelpbot')
    #     queue_url = response['QueueUrl']
    #     response = sqs.send_message(
    #         QueueUrl=queue_url,
    #         MessageAttributes={
    #             'Location': {
    #             'DataType': 'String',
    #             'StringValue': city
    #             },
    #             'Cuisine': {
    #             'DataType': 'String',
    #             'StringValue': cuisine_type
    #             },
    #             'reservation_date': {
    #             'DataType': 'String',
    #             'StringValue': date
    #             },
    #             'reservation_time': {
    #             'DataType': 'String',
    #             'StringValue': reservation_time
    #             },
    #             'numberOfPeople': {
    #             'DataType': 'Number',
    #             'StringValue': str(numberOfPeople)
    #             },
    #             'PhoneNumber': {
    #             'DataType': 'String',
    #             'StringValue': str(phone)
    #             }
    #         },
    #         MessageBody=(
    #             'Customer details for restaurant reservation'
    #         )
    #     )

    #     print('The message id for the response msg is {}'.format(response['MessageId']))
        
        # return close(intent_request['sessionAttributes'],
        #          'Fulfilled',
        #          {'contentType': 'PlainText',
        #           'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'})
            
    # after fulfilment calling sqs
    sendMsg(slots)
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you! You will recieve suggestion shortly'})
    



# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions(intent_request)
    elif intent_name == 'GreetingIntent':
        ans = sendMsg()
        return (ans)
        return greetings(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    # logger.debug('dispatch userId={}, intentName={}'.format(event['userId'], event['currentIntent']['name']))
    # intent_name = event['currentIntent']['name']
    # ans =    {
    #     'dialogAction': {
    #         "type": "ElicitIntent",
    #         'message': {
    #             'contentType': 'PlainText',
    #             'content': intent_name}
    #     }
    # }
    # return(ans)

    return dispatch(event)
    
    
    
