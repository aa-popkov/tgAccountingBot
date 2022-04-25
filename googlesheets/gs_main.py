import configparser

import googleapiclient.discovery
from google.oauth2 import service_account


config = configparser.ConfigParser()
config.read('config.ini')
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.get('google_sheets', 'sheets_id')
SERVICE_ACCOUNT_FILE = 'cred.json'


def get_value(range: list) -> list:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    range = range
    table = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    resp = table.spreadsheets().values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=range).execute()
    return resp.get('valueRanges', [])[0]['values']


def set_value(values: list, range: str):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    table = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    values = values
    data = [
        {
            'range': range,
            'values': values
        },
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    result = table.spreadsheets().values().batchUpdate(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
    # print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


def main():
    pass
    # range = [
    #     "Data!A1:A",
    # ]
    #
    # mass = get_value(range)
    #
    # print(len(mass))
    #
    # range = "Лист1!A5:C5"
    # set_value([[3, "va", 2000]], range)


if __name__ == '__main__':
    main()