from django.core.exceptions import ObjectDoesNotExist


class PriceDoesNotExistOnDate(ObjectDoesNotExist):
    """The requested price of a product does not exist on this date"""
    pass


class RetryExhausted(Exception):
    """All retry attempts have been exhausted for an API call"""
    pass
