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
from helper import parse_webhook_request, generate_webhook_response, get_api_key, send_email
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
        return 'You have no course grades right now!'

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


def process_files(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    canvas = CanvasAPI(api_key)
    file_name = req['session']['params']['file_name']
    class_name = req['session']['params']['class_name']

    attempts = 1
    prev_found_ = None
    if 'file_codes' in req['session']['params']:
        attempts = int(req['session']['params']['attempts']) + 1
        prev_found_ = req['session']['params']['file_codes']

    # Get 3 closest matching files from closest matching course
    close_files, course_id = canvas.get_closest_files(file_name, class_name, prev_found_)
    hold_files = []
    if close_files == "":
        return "The class specified does not have any files.", hold_files, course_id, attempts
    # Generate response
    response = "Please select the file you were looking for by saying its number, or say \"none\" and we'll look again.\n"
    for i, file in enumerate(close_files):
        response += str(i + 1) + ') ' + str(file) + '\n'
        hold_files.append(file.id)

    return response, hold_files, course_id, attempts


def send_file(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    canvas = CanvasAPI(api_key)
    # Retrieve stored information from last turn 
    held_files = req['session']['params']['file_codes']
    num_selected = int(req['session']['params']['file_num'])
    if num_selected <= 0 or num_selected >= 4:
        return "Please select a file number between 1 and 3"

    file_id = held_files[num_selected - 1]
    course_id = req['session']['params']['course_id']

    # Temporarily downloads target file and gets user's email for sending file
    receiver_address, canvas_url = canvas.fetch_file_to_send(course_id, file_id)
    if not send_email(receiver_address, canvas_url):
        return "<a href=\"" + canvas_url + "\" target=\"_blank\">Click here to view and download your file</a>"

    response = "<a href=\"" + canvas_url + "\" target=\"_blank\">Click here to view and download your file</a>"
    response += "The link has also been sent to the email associated with your Canvas account to view on other devices."
    return response


def process_announcements(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()

    course = None
    if 'class_name' in req['intent']['params']:
        course = req['intent']['params']['class_name']

    canvas = CanvasAPI(api_key)
    announcements, contextCodeMap = canvas.get_filtered_announcements(course=course)  # Specified course or all if nothing specified
    if len(announcements) == 0:
        return 'There are no announcements from your courses!', []

    response = 'Here are the most recent course announcements: \n'
    full_messages = []
    for i, announcement in enumerate(announcements):
        response += str(i + 1) + ') ' + str(announcement.title) + ' (' + str(contextCodeMap[announcement.context_code]) + ') \n'
        full_messages.append(str(announcement.message))
    response += 'If you want to view the full message from one of the announcements, respond with the corresponding number \n'

    return response, full_messages


def find_assignment(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()
    canvas = CanvasAPI(api_key)
    # Extract relevant info from intent params 
    class_name = req['session']['params']['class_name']
    assignment_name = req['session']['params']['assignment_name']

    assn_obj = canvas.get_assignment_info(class_name, assignment_name)

    if assn_obj['score'] == "":
        return "No score found for " + assn_obj['name']
    else:
        return "You got a " + str(assn_obj['score']) + "/" + str(assn_obj['points_possible'])  + " (" + assn_obj['grade'] + ") on " + assn_obj['name']


def get_full_announcement(req):
    full_messages = req['session']['params']['full_messages']
    num_selected = int(req['session']['params']['announcement_num'])
    if num_selected <= 0 or num_selected >= len(full_messages):
        return "Please select an announcement number between 1 and " + str(len(full_messages))

    response = full_messages[num_selected - 1]
    return response


def use_bert(req):
    try:
        api_key = get_api_key()
    except:
        print('no api key!')
        raise Exception()
    
    canvas = CanvasAPI(api_key)

    # Should be set up in dialogflow as intent because we need to extract class name (can't do that with no-match)
    class_name = req['session']['params']['class_name']
    # Gets the syllabus in whatever format it is stored in and returns in string
    syllabus = canvas.get_syllabus(class_name)

    # Use bert here, the above already takes like 3 seconds, this might take awhile

    return syllabus


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
    if 'intent' in req:
        print(json.dumps(req['intent']))
    if 'session' in req:
        print(json.dumps(req['session']))

    if req['tag'] == 'todo':
        resp = process_todo(req)
        return json.dumps(generate_webhook_response([resp], request_json))
    elif req['tag'] == 'grades':
        resp = process_grades(req)
        return json.dumps(generate_webhook_response([resp], request_json))
    elif req['tag'] == 'assignment_grade':
        resp = find_assignment(req)
        return json.dumps(generate_webhook_response([resp], request_json))
    elif req['tag'] == 'files':
        resp, hold_files, course_id, attempts = process_files(req)
        request_json['sessionInfo']['parameters']['file_codes'] = hold_files
        request_json['sessionInfo']['parameters']['course_id'] = course_id
        request_json['sessionInfo']['parameters']['attempts'] = attempts
        return json.dumps(generate_webhook_response([resp], request_json, changeSessionParams=True))
    elif req['tag'] == 'send_file':
        resp = send_file(req)
        return json.dumps(generate_webhook_response([resp], request_json))
    elif req['tag'] == 'announcements':
        resp, full_messages = process_announcements(req)
        if 'parameters' not in request_json['sessionInfo']:
            request_json['sessionInfo']['parameters'] = {}
        request_json['sessionInfo']['parameters']['full_messages'] = full_messages
        return json.dumps(generate_webhook_response([resp], request_json, changeSessionParams=True))
    elif req['tag'] == 'get_full_announcement':
        resp = get_full_announcement(req)
        return json.dumps(generate_webhook_response([resp], request_json))
    elif req['tag'] == 'syllabus':
        resp = use_bert(req)
        return json.dumps(generate_webhook_response([resp], request_json))

    # no intent found
    raise Exception()
