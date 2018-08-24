from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file

import difflib
import subprocess

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
        response = service.scripts().run(body=request, scriptId=SCRIPT_ID).execute()
        try:
            result = response['response']['result']
            return result
        except KeyError:
            try:
                print(response['error']['details'][0]['errorMessage'])
                return None
            except KeyError:
                print(response)
                return None
    except errors.HttpError as e:
        print('PROCESS FAILED. SEE BELOW:')
        print(str(e.content))
        return None


def run_local_comparison(tables, fair_tables):
    result = list()
    additional = None
    if len(tables) > len(fair_tables):
        additional = [i for i in range(len(fair_tables), len(tables))]
    for key, fair_key in zip(tables.keys(), fair_tables.keys()):
        table = tables[key]
        fair_table = fair_tables[fair_key]
        same = (table == fair_table)
        if not same:
            result.append(key[1])
    if additional:
        result.extend(additional)
    if len(result) > 0:
        return result
    else:
        return None


def create_diff(fair, current, filename):

    command = 'pandoc ' + fair + ' -t markdown'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = proc.communicate()
    if res[1]:
        print('PROCESS FAILED. SEE BELOW:')
        print(str(res[1]))
        return None  # sending stderr output to user
    else:
        fair_copy = res[0]
        html_output = filename + "_rmdupd.html"
        filename += "_fair_md_rmdupd.md"
        with open(filename, 'wb') as fair_md_file:
            fair_md_file.write(fair_copy)
        with open(filename, 'r') as tolines, open(current, 'r') as fromlines, open(html_output, 'w') as out:
            fromlines = fromlines.readlines()
            tolines = tolines.readlines()
            comparator = difflib.HtmlDiff()
            result = comparator.make_file(fromlines=fromlines, tolines=tolines)
            out.write(result)


def run_local_text_comparison(text, fair_text):
    current = frozenset(text)
    actual = frozenset(fair_text)
    difference = actual ^ current
    deleted = current & difference
    added = actual & difference
    return {'deleted': tuple(deleted), 'added': tuple(added)}
