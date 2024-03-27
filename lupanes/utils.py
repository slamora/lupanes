import gspread
from django.conf import settings

CREDENTIALS_PATH = settings.LUPIERRA_GSPREAD_AUTH_PATH

DOC_URL = settings.LUPIERRA_CUSTOMERS_BALANCE_URL


def load_spreadsheet():
    gc = gspread.service_account(filename=CREDENTIALS_PATH)
    sh = gc.open_by_url(DOC_URL)
    worksheet = sh.get_worksheet(0)
    return worksheet


def search_nevera_balance(nevera):
    worksheet = load_spreadsheet()
    values = worksheet.get_all_values()

    for row in values:
        if row[0] == nevera:
            return row[1]

    return "N/A"
