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


def process_grades(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    courses = None
    # TODO: Implement mapper from course name/code to courseID
    if 'courses' in req['intentInfo']['parameters']:
        courses = req['intentInfo']['parameters']['courses']

    canvas = CanvasAPI(api_key)
    grades = canvas.get_course_grades(courses) # Specified course grades or all if nothing specified
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
            formatted_grades.append('{0}% in {1}'.format(grade['score'], grade['name']))
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

def process_files(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    canvas = CanvasAPI(api_key)
    file_name = req["intent"]['params']['file_name']
    class_name = req["intent"]['params']['class_name']

    # Get 3 closest matching files from closest matching course
    close_files, course_id = canvas.get_closest_files(file_name, class_name)
    hold_files = []
    if close_files == "":
        return "The class specified does not have any files.", hold_files, course_id
    # Generate response
    response = ''
    for i, file in enumerate(close_files):
        response += str(i + 1) + ') ' + str(file) + '\n'
        hold_files.append(file.id)

    return response, hold_files, course_id


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
    elif req['tag'] == 'files':
        resp, hold_files, course_id = process_files(req)
        request_json['sessionInfo']['parameters']['file_codes'] = hold_files
        request_json['sessionInfo']['parameters']['course_id'] = course_id
        return json.dumps(generate_webhook_response([resp], request_json))

    # no intent found
    raise Exception()
