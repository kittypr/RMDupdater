import os

from oauth2client import file as oauth_file, client, tools

SCOPES = ['https://www.googleapis.com/auth/documents']


def create():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(dir_path + '\credentials.json', SCOPES)  # fix this
        tools.run_flow(flow, store)


if __name__ == '__main__':
    create()
