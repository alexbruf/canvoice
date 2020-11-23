from unittest.mock import Mock
from unittest import TestCase, mock
import main
import json
from canvasapi.calendar_event import CalendarEvent
from canvasapi.file import File
from datetime import datetime

now = datetime.now()

@mock.patch('main.CanvasAPI.get_todo')
def test_todo_intent(mocked_api):
    f = open('test_request.json', 'rb')
    if not f:
        raise Exception()

    req = json.load(f)
    req['fulfillment_info'] = {'tag': 'todo'}
 
    mocked_api.return_value = [CalendarEvent(None, {
                'title': 'test',
                'start_at': now.isoformat()
            })]
    assert main.process_todo(req) == 'You have test on ' + now.isoformat()
    mocked_api.assert_called_once()

# #TODO
@mock.patch('main.CanvasAPI.get_todo')
def test_backend_activate_todo(mocked_api):
    name = 'test'
    f = open('test_request.json', 'rb')
    if not f:
        raise Exception()

    data = json.load(f) # replace with request
    data['fulfillmentInfo'] = {'tag': 'todo'}
    mocked_api.return_value = [CalendarEvent(None, {
                'title': 'test',
                'start_at': now.isoformat()
            })]
    req = Mock(get_json=Mock(return_value=data), args=data)

    # Call tested function
    test_resp = {
        'fulfillment_response': {
            'messages': [{'text': {'text:' ['You have test on ' + now.isoformat()]}}],
            'merge_behavior': 'REPLACE'
        }
    }
    assert json.loads(main.backend_activate(req)) == test_resp ## replace with good test


@mock.patch('main.CanvasAPI.get_course_grades')
def test_grades_intent(mocked_api):
  f = open('test_request.json', 'rb')
  if not f:
    raise Exception()

  req = json.load(f)
  req['fulfillment_info'] = {'tag': 'grades'}

  # Not sure if i did this correctly
  mocked_api.return_value = [dict([
    ('id', 0),
    ('name', 'test_class'),
    ('score', 100.0),
  ])]
  assert main.process_grades(req) == 'You have a 100.0% in test_class'
  mocked_api.assert_called_once()


@mock.patch('main.CanvasAPI.get_closest_files')
def test_files_intent(mocked_api):
    f = open('test_request.json', 'rb')
    if not f:
        raise Exception()

    req = json.load(f)
    req['fulfillment_info'] = {'tag': 'files'}

    mocked_api.return_value = [File(None, {
                'filename': 'test.txt'
            }),
            File(None, {
                'filename': 'test2.txt'
            })]

    assert main.process_files(req) == 'tt'
    mocked_api.assert_called_once()
