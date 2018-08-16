from oauth2client import file as oauth_file, client, tools

SCOPES = ['https://www.googleapis.com/auth/documents']


def create():
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        tools.run_flow(flow, store)


if __name__ == '__main__':
    create()