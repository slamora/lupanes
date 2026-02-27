import time
import random
import logging
from functools import wraps

import gspread
from gspread.exceptions import APIError
import requests.exceptions
from django.conf import settings

from lupanes.exceptions import RetryExhausted

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = settings.LUPIERRA_GSPREAD_AUTH_PATH
DOC_URL = settings.LUPIERRA_CUSTOMERS_BALANCE_URL


def retry_on_gspread_error(max_retries=4, base_delay=1.0):
    """Retry decorator with exponential backoff for gspread API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (APIError, requests.exceptions.RequestException) as e:
                    if attempt == max_retries - 1:
                        raise RetryExhausted(f"Failed after {max_retries} attempts: {e}")

                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, 0.1 * delay)
                    sleep_time = delay + jitter

                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
        return wrapper
    return decorator


@retry_on_gspread_error(max_retries=4, base_delay=1.0)
def load_spreadsheet():
    gc = gspread.service_account(filename=CREDENTIALS_PATH)
    sh = gc.open_by_url(DOC_URL)
    worksheet = sh.get_worksheet(0)
    return worksheet


def search_nevera_balance(nevera):
    worksheet = load_spreadsheet()
    values = worksheet.get_all_values()

    nevera = nevera.lower()
    for row in values:
        current = row[0].strip().lower()
        if current == nevera:
            return row[1]

    return "N/A"
