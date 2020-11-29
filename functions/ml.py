from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import textract
import os

model_name = "deepset/roberta-base-squad2"

cache_dir='./model_cache/'

def load_bert():
  ''' returns a bert object '''
  os.environ['TRANSFORMERS_CACHE']=cache_dir
  nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
  return nlp

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


def run_bert(bert, context):
  res = bert(context)
  return {
    'score': res['score'],
    'answer': res['answer']
  }
