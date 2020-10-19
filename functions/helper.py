import json

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
    parsed['detect_intent_response_id'] = request_json.get('detect_intent_response_id', '')
    intent_info = request_json.get('intent_info')
    if len(intent_info) > 0:
        parsed['intent'] = {
            'intent_id': intent_info[0]['last_matched_intent']
        }

        parsed['intent']['params'] = {}
        params = intent_info[0]['parameters']
        for param in params.keys():
            parsed['intent']['params'][param] = params[param]['resolved_value']

    parsed['tag'] = request_json.get('fulfillment_info', '')
    
    
    session_info = request_json.get('session_info')
    if session_info:
        parsed['session'] = {
            'session_id': session_info['session'],
            'params': {}
        }
        params = session_info['parameters']
        for param in params.keys():
            parsed['session']['params'][param] = params[param]
    
    return parsed

def get_api_key():
  with open('../api_key.json', 'rb') as file:
    j = json.load(file)
    return j['canvas_api_key']
  
  raise Exception()

def generate_webhook_response(messages, request_json):
    resp = {}
    resp['page_info'] = request_json['page_info']
    resp['session_info'] = request_json['session_info']
    resp['payload'] = request_json['payload']
    resp['fulfillment_response'] =  {
        'messages': messages,
        'merge_behavior': 'REPLACE'
    }

    return resp