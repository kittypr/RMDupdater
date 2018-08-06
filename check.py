from apiclient import errors
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/documents']
API_SERVICE_NAME = 'script'
API_VERSION = 'v1'
SCRIPT_ID = 'MfUCDEAFYCuUxb_9IPU7Cho8zoCCdfz7A'


def run_comparison(gdoc_id, tables):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build(API_SERVICE_NAME, API_VERSION, http=creds.authorize(Http()))

    # Call the Apps Script API
    try:
        # call for comparing script
        request = {'function': 'compare', 'parameters': [gdoc_id, tables]}
        response = service.scripts().run(body=request,
                                         scriptId=SCRIPT_ID).execute()
        print(response)
        return response['response']['result']
    except errors.HttpError as e:
        print(str(e.content))
