import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib


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

def generate_webhook_response(messages, request_json, changeSessionParams=False):
    '''
    messages: string[]
    request_json: json
    '''

    # return messages[0]
    resp = {}
    # resp['pageInfo'] = request_json.get('pageInfo', None)
    # resp['payload'] = request_json.get('payload', None)
    # resp['fulfillmentText'] = messages[0]
    resp['fulfillment_response'] =  {
        'messages': [{
            'text': {'text': messages}
        }],
        'merge_behavior': 'REPLACE'
    }
    if changeSessionParams == True:
        resp['sessionInfo'] = request_json.get('sessionInfo', None)

    return resp

def send_email(file_name, receiver_address):
    try:
        mail_content = '''Hello, your file should be attached to this email. Thanks for using CanVoice!
        '''
        #The mail addresses and password 
        sender_address = 'canvoiceemail@gmail.com'
        sender_pass = ""
        f = open('../app_pw.txt', 'r')
        sender_pass = f.readline()
        f.close()

        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'CanVoice File Email'
        #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = file_name
        attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        name, ext = os.path.splitext(attach_file_name)
        if ext == ".pdf":
            payload = MIMEBase('application', 'pdf')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        #add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        os.remove(file_name)
        return True
    except:
        os.remove(file_name)
        return False