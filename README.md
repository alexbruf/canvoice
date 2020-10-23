# canvoice

cloud function id: canvoice-backend
gcp project id: canvoice-292621

gcloud auth login
gcloud config set project canvoice-292621

to authorize for dialogflow download the JS client key file and run the following commands:
        gcloud auth activate-service-account --key-file=<keyfile.json>
        gcloud auth print-access-token
    Use the printed token in the website input box to access DialogFlow

canvas python api: https://canvasapi.readthedocs.io/en/stable/getting-started.html

Make sure you put your canvas api key in a file called "api_key.json" at the root level with contents

```
{
  "canvas_api_key": "<your api key>"
}
```

How a fullfillment_response is supposed to look:
```
{
            'fulfillment_response': {
                'messages': [
                       { 
                           'text': {'text': ['test message 2']}
                       },
                    ],
                    'merge_behavior': 'REPLACE'
                },
            'payload': {
                'test': 'val'
            }
        }
```
