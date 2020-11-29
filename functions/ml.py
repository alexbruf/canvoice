import textract
import requests

bert_url = 'http://bert.pureuniversaltruth.com:8080'

def prepare_context(question, pdf_encoded_string):
  with open('/tmp/textr.pdf', 'w') as f:
    f.write(pdf_encoded_string)
  
  text = textract.process('/tmp/textr.pdf')
  text = text.decode('ascii', 'ignore')
  text = ' '.join(text.split()).replace('\r', ' ').replace('\n', ' ')
  QA_input = {
      'question': question,
      'context': text
  }

  return QA_input

def run_bert(context):
  r = requests.post(bert_url, json=context)
  try: 
    resp = r.json()
  except Exception as e:
    print(e)
    resp = {'score': 0.0, 'answer': 'no answer'}
  return resp
