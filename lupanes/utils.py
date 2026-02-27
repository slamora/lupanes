import time
import random
import logging
from functools import wraps

import gspread
from gspread.exceptions import APIError
import requests.exceptions
from django.conf import settings
from django.core.cache import cache

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


def _get_nevera_cache_key(nevera_name):
    """Generate cache key for customer balance"""
    return f"nevera_balance:{nevera_name.lower()}"


@retry_on_gspread_error(
    max_retries=settings.LUPIERRA_GSPREAD_MAX_RETRIES,
    base_delay=settings.LUPIERRA_GSPREAD_BASE_DELAY
)
def load_spreadsheet():
    gc = gspread.service_account(filename=CREDENTIALS_PATH)
    sh = gc.open_by_url(DOC_URL)
    worksheet = sh.get_worksheet(0)
    return worksheet


def search_nevera_balance(nevera):
    """
    Search for customer balance in Google Sheet with caching and retry.

    On cache miss, fetches the entire spreadsheet and caches ALL customers
    to minimize API calls. Subsequent requests for any customer hit the cache.

    Args:
        nevera: Customer name to search for (case-insensitive)

    Returns:
        str: Balance value or "N/A" if not found
    """
    requested_nevera_name = nevera.lower()
    cache_key = _get_nevera_cache_key(requested_nevera_name)

    cached_value = cache.get(cache_key)
    if cached_value is not None:
        logger.debug(f"Cache hit for {requested_nevera_name}")
        return cached_value

    logger.debug(f"Cache miss for {requested_nevera_name}, fetching spreadsheet and caching all customers")
    worksheet = load_spreadsheet()
    values = worksheet.get_all_values()

    result = "N/A"
    for row in values:
        if len(row) >= 2:
            row_nevera_name = row[0].strip().lower()
            row_balance = row[1]
            row_cache_key = _get_nevera_cache_key(row_nevera_name)
            cache.set(row_cache_key, row_balance, timeout=settings.LUPIERRA_BALANCE_CACHE_TTL)

            if row_nevera_name == requested_nevera_name:
                result = row_balance

    # Cache the result (including "N/A" if not found)
    cache.set(cache_key, result, timeout=settings.LUPIERRA_BALANCE_CACHE_TTL)
    return result
