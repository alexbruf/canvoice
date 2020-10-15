# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

# [START functions_helloworld_http]
# [START functions_http_content]
from flask import escape

# [END functions_helloworld_http]
# [END functions_http_content]

# [START functions_helloworld_get]
def hello_get(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    return 'Hello World!'    
# [END functions_helloworld_get]


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


def generate_webhook_response(messages, request_json):
    resp = {}
    resp['page_info'] = request_json['page_info']
    resp['session_info'] = request_json['session_info']
    resp['payload'] = request_json['payload']
    resp['fulfillment_response'] =  {
        'messages': messages,
        'merge_behavior': 'REPLACE'
    }

def process_todo(req):
    return 'Nothing new!'


def backend_activate(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_json = request.get_json()
    if not request.args:
        raise Exception()
    
    req = parse_webhook_request(request_json)

    if req['tag'] == 'todo':
        resp = process_todo(req)
        return generate_webhook_response([resp], request_json)

    # no intent found
    raise Exception()

