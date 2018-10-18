from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file

import difflib


CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/documents']
API_SERVICE_NAME = 'script'
API_VERSION = 'v1'
SCRIPT_ID = 'MfUCDEAFYCuUxb_9IPU7Cho8zoCCdfz7A'


def run_comparison(function_name, parameters):  # left for future functionality
    """Calls the Apps Script API.

    :param function_name: function name that will be called in google apps script.
    :param parameters: function's parameters.
    :return: if succeed:
                         result: list with result of running apps scripts funtion.
             if failed:
                        None
    """
    store = oauth_file.Storage('token.json')
    creds = store.get()
    service = build(API_SERVICE_NAME, API_VERSION, http=creds.authorize(Http()))
    # Call the Apps Script API
    try:
        # call for comparing script
        request = {'function': function_name, 'parameters': parameters}
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
    """Compares two tuples of tuples which represent tables.

    :param tables: tables from current reports.
    :param fair_tables: tables from fair copy from gdoc.
    :return: result: list of tuples of context and ancestor that refer to tables that differs from tables in fair copy.
    """
    result = list()
    for current, fair in zip(tables, fair_tables):
        if current[0] != fair[0]:
            result.append(current[1])
    if len(tables) > len(fair_tables):
        result.extend([current[1] for current in tables[len(fair_tables):]])
    return result


def run_local_text_comparison(text, fair_text):
    """Finds deleted and new blocks.

    :param text: text blocks from current report.
    :param fair_text: text blocks from fair copy from gdoc.
    :return: {deleted: tuple of deleted blocks, added: tuple of new blocks},
             changed = list of indexes in which difference was found.
    """
    changed = list()
    current_list = [item[0] for item in text]
    current = frozenset(current_list)
    actual = frozenset([item[0] for item in fair_text])
    difference = actual ^ current
    deleted = current & difference
    added = actual & difference
    deleted = tuple(deleted)
    added = tuple(added)
    for deleted_text in deleted:
        changed.append(current_list.index(deleted_text))
    return {'deleted': deleted, 'added': added}, changed


def create_diff(fromlines, tolines, filename):
    """Creates diff file.

    :param fromlines: current blocks.
    :param tolines: fair copy's blocks.
    :param filename: unique prefix.
    :return: -
    """
    fromlines = list([text[0] for text in fromlines])
    tolines = list([text[0] for text in tolines])
    html_output = filename + '_rmdupd.html'
    with open(html_output, 'wb') as out:
        comparator = difflib.HtmlDiff(tabsize=4)
        result = comparator.make_file(fromlines=fromlines, tolines=tolines,
                                      fromdesc='Current report', todesc='Clean copy on Gdoc', context=True, numlines=1)
        result += '\n'
        out.write(result.encode('UTF-8'))

