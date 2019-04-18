import datetime
from pytz import timezone


# TODO: Test and consider about time zone issue.

def datetime_to_timestamp(dt):
    epoch = datetime.datetime(1970, 1, 1, tzinfo=timezone('UTC'))
    return int((dt - epoch).total_seconds())


def timestamp_to_datetime(ts):
    return datetime.datetime.fromtimestamp(ts)
