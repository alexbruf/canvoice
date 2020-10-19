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
from helper import parse_webhook_request, generate_webhook_response, get_api_key
from api import CanvasAPI
from datetime import datetime
from flask import escape, jsonify
import json

def process_todo(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    canvas = CanvasAPI(api_key)
    todos = canvas.get_todo() # next 7 days of todos
    if len(todos) == 0:
        return 'You have nothing new due!'

    todo_on = ['{0} on {1}'.format(todo.title, todo.start_at) for todo in todos]
    return 'You have ' + ' and '.join(todo_on)


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
    if not request_json:
        raise Exception()
    
    req = parse_webhook_request(request_json)
    print(json.dumps(request_json))
    print(json.dumps(req))

    if req['tag'] == 'todo':
        resp = process_todo(req)
        return json.dumps(generate_webhook_response([resp], request_json))

    # no intent found
    raise Exception()

