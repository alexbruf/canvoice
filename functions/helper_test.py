from helper import parse_webhook_request, generate_webhook_response
import json

def test_parse_request():
    f = open('test_request.json', 'rb')
    if not f:
        raise Exception()

    req = json.load(f)

    resp = parse_webhook_request(req)
    
    assert resp == {
        'detect_intent_response_id': 'test_id',
        'intent': {
            'intent_id': 'test_intent_id',
            'params': {
                "test_param0":  "test_param_value",
                "test_param1": 0,
                "test_param2": False
            }
        },
        'tag': 'todo', # use this to determine action to take
        'session': {
            'session_id': 'test_session_id',
            'params': {
                "test_param0":  "test_param_value",
                "test_param1": 0,
                "test_param2": False
            }
        }
    }


def test_generate_response():
    f = open('test_request.json', 'rb')
    if not f:
        raise Exception()

    req = json.load(f)

    resp = generate_webhook_response(['test message'], req)

    test_resp = {
        'session_info': req['session_info'],
        'fulfillment_response': {
            'messages': ['test message'],
            'merge_behavior': 'REPLACE'
        },
        'page_info': None,
        'payload': None
    }

    assert resp == test_resp