import dateutil.parser
from datetime import datetime
import pytz


Brussels = pytz.timezone('Europe/Brussels')


def parse_time(obj):
    if isinstance(obj, str):
        obj = dateutil.parser.parse(obj)
    elif isinstance(obj, int) or isinstance(obj, float):
        obj = datetime.fromtimestamp(obj)

    if obj.tzname():
        tt = obj.astimezone(Brussels).timetuple()[:6]
        obj = datetime(*tt)
    return obj


def make_style(before, after='\x0F'):
    if after is None:
        after = before

    def inner(*args):
        text = ''.join(map(str, args))
        if text[0].isdigit():
            text = " " + text
        return '{}{}{}'.format(before, text, after)
    return inner
