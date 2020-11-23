import json
import os


def parse_webhook_request(request_json):
    '''
    Should return a parsed object:
    {
        'detect_intent_response_id': string,
        'intent': {
            'intent_id': string,
            'params': map<string, Value>
        },
        'tag': string, # use this to determine action to take
        'session': {
            'session_id': string,
            'params': map<string, Value>
        }
    }
    '''
    parsed = {}
    parsed['detect_intent_response_id'] = request_json.get('detectIntentResponseId', '')
    intent_info = request_json.get('intentInfo', None)
    if intent_info:
        parsed['intent'] = {
            'intent_id': intent_info['lastMatchedIntent']
        }

        parsed['intent']['params'] = {}
        params = intent_info.get('parameters', {})
        for param in params.keys():
            parsed['intent']['params'][param] = params[param]['resolvedValue']

    parsed['tag'] = request_json.get('fulfillmentInfo', {}).get('tag')
    
    
    session_info = request_json.get('sessionInfo')
    if session_info:
        parsed['session'] = {
            'session_id': session_info['session'],
            'params': {}
        }
        params = session_info.get('parameters', {})
        for param in params.keys():
            parsed['session']['params'][param] = params[param]
    
    return parsed


def get_api_key():
    func_name = os.environ.get('CANVAS_API_KEY', None)
    if func_name:
        #production environment
        api_key = os.environ.get('CANVAS_API_KEY', None)
        if api_key:
            return api_key
        else:
            raise Exception()

    with open('../api_key.json', 'rb') as file:
        j = json.load(file)
        return j['canvas_api_key']

    raise Exception()


def generate_webhook_response(messages, request_json):
    '''
    messages: string[]
    request_json: json
    '''

    # return messages[0]
    resp = {}
    # resp['pageInfo'] = request_json.get('pageInfo', None)
    # resp['sessionInfo'] = request_json.get('sessionInfo', None)
    # resp['payload'] = request_json.get('payload', None)
    # resp['fulfillmentText'] = messages[0]
    resp['fulfillment_response'] =  {
        'messages': [{
            'text': {'text': messages}
        }],
        'merge_behavior': 'REPLACE'
    }

    return resp