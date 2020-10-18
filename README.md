# canvoice

cloud function id: canvoice-backend
gcp project id: canvoice-292621

gcloud auth login
gcloud config set project canvoice-292621

to authorize for dialogflow download the JS client key file and run the following commands:
        gcloud auth activate-service-account --key-file=<keyfile.json>
        gcloud auth print-access-token
    Use the printed token in the website input box to access DialogFlow