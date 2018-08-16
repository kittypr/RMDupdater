from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/documents']
API_SERVICE_NAME = 'script'
API_VERSION = 'v1'
SCRIPT_ID = 'MfUCDEAFYCuUxb_9IPU7Cho8zoCCdfz7A'


def run_comparison(gdoc_id, tables):
    """Calls the Apps Script API.
    """
    store = oauth_file.Storage('token.json')
    creds = store.get()
    service = build(API_SERVICE_NAME, API_VERSION, http=creds.authorize(Http()))
    # Call the Apps Script API
    try:
        # call for comparing script
        request = {'function': 'compare', 'parameters': [gdoc_id, tables]}
        response = service.scripts().run(body=request,
                                         scriptId=SCRIPT_ID).execute()
        print(response)
        return response['response']['result']
    except errors.HttpError as e:
        print('PROCESS FAILED. SEE BELOW:')
        print(str(e.content))
        return None
