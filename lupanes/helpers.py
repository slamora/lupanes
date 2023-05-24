import datetime
from django.utils import timezone


def clean_month(value):
    today = timezone.now().date()
    if value is None:
        value = today.month
    try:
        value = datetime.date(year=today.year, month=int(value), day=1)
    except ValueError:
        value = today

    return value
