import datetime
import time


def date_to_ms(date: datetime):
    # timestamp = int(round(date.timestamp() * 1000))
    timestamp = int(round(date.timestamp()))
    return timestamp


def get_current_time():
    return date_to_ms(datetime.datetime.now())


def current_date_ms():
    return int(round(time.time()))
