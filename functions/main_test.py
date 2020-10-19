from unittest.mock import Mock

import main

def test_todo_intent():
    req_spoof =  {
        'detect_intent_response_id': 'string',
        'intent': {
            'intent_id': 'string',
            'params': {}
        },
        'tag': 'todo', # use this to determine action to take
        'session': {
            'session_id': 'string',
            'params': {}
        }
    }
    assert main.process_todo(req_spoof) == 'Nothing new!'

#TODO
def test_backend_activate():
    name = 'test'
    data = {'name': name} # replace with request
    req = Mock(get_json=Mock(return_value=data), args=data)

    # Call tested function
    assert main.backend_activate(req) == 'Hello!' ## replace with good test