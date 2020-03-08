import datetime
from django.utils import timezone
import calendar

def get_month_range(t0=None):
    t0 = t0 if t0 is not None else timezone.now()
    t1 = datetime.datetime(t0.year, t0.month, 1)
    t2 = datetime.datetime(t0.year + int(t0.month / 12), t0.month % 12 + 1 , 1)
    return (t1, t2)

def get_today(t0=None):
    today = t0 if t0 is not None else timezone.now()
    return today - datetime.timedelta(0, today.hour*3600 + today.minute*60 + today.second, today.microsecond)
