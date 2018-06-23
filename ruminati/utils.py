from dateutil.parser import parse
from dateutil.tz import UTC


def parse_time_in(time, tz):
    return parse(time, ignoretz=True).replace(tzinfo=tz).time()


def parse_naive_datetime(datetime_str):
    return parse(datetime_str, ignoretz=True)


def assert_naive(datetime):
    assert datetime.tzinfo is None


def parse_aware_datetime(datetime, tz):
    return parse(datetime, ignoretz=True).replace(tzinfo=tz)


def parse_to_utc(datetime, tz):
    return parse(datetime, ignoretz=True).replace(tzinfo=tz).astimezone(UTC)


def parse_date_in(date, tz):
    return parse(date, ignoretz=True).replace(tzinfo=tz).date()
