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
from datetime import datetime, timedelta
from flask import escape, jsonify
import json

def process_todo(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    course = None
    if 'class_name' in req['intent']['params']:
        course = req['intent']['params']['class_name']

    canvas = CanvasAPI(api_key)
    todos = canvas.get_todo(course=course) # next 7 days of todos
    if len(todos) == 0:
        return 'You have nothing due in the next week!'

    todo_on = []
    for todo in todos:
        formattedDate = datetime.strptime(todo.start_at, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=5)
        courseName = todo.context_name.split()[0] + ' ' + todo.context_name.split()[1]
        todo_on.append('{0} ({1}) on {2}'.format(
            todo.title,
            courseName,
            formattedDate.strftime('%m/%d %I:%M%p'),
        ))

    if len(todo_on) == 1:
        return 'You have ' + todo_on[0]
    elif len(todo_on) == 2:
        return 'You have ' + ' and '.join(todo_on)
    else:
        response = 'You have ' + todo_on[0]
        for formatted_todo in todo_on[1:-1]:
            response += ', ' + formatted_todo
        response += ', and ' + todo_on[-1]
        return response


def process_grades(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    course = None
    if 'class_name' in req['intent']['params']:
        course = req['intent']['params']['class_name']

    canvas = CanvasAPI(api_key)
    grades = canvas.get_course_grades(course) # Specified course grades or all if nothing specified
    numGrades = len(grades)
    if numGrades == 0:
        print('You have no course grades right now!')

    # Format response string based on
    formatted_grades = []
    none_grades = []
    for grade in grades:
        if grade['score'] == None:
            none_grades.append(grade['name'])
        else:
            formatted_grades.append('{0}% in {1}'.format(grade['score'], grade['code']))
    numFormatted = len(formatted_grades)
    numNone = len(none_grades)
    assert numGrades == (numFormatted + numNone)

    response = ''
    # Output well-formed response depending on number of valid and 'None' grades received
    if numFormatted == 0:
        response += 'I couldn\'t find any grade for ' + none_grades[0]
        if numNone > 1:
            for none_grade in none_grades[1:(numNone-1)]:
                response += ', ' + none_grade
            response += ', or ' + none_grades[numNone-1]
        response += '.'
    else:
        response += 'You have a ' + formatted_grades[0]
        if numFormatted > 1:
            for formatted_grade in formatted_grades[1:(numFormatted-1)]:
                response += ', a ' + formatted_grade
            response += ', and a ' + formatted_grades[numFormatted-1]
        response += '. '
        if numNone > 0:
            response += 'I couldn\'t find any grade for ' + none_grades[0]
            if numNone > 1:
                for none_grade in none_grades[1:(numNone-1)]:
                    response += ', ' + none_grade
                response += ', or ' + none_grades[numNone-1]
            response += '.'

    return response


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
    elif req['tag'] == 'grades':
        resp = process_grades(req)
        return json.dumps(generate_webhook_response([resp], request_json))

    # no intent found
    raise Exception()
