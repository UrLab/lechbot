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


class IRCColors:
    bold = staticmethod(make_style('\x02', '\x02'))
    red = staticmethod(make_style('\x035', '\x03'))
    green = staticmethod(make_style('\x033', '\x03'))
    yellow = staticmethod(make_style('\x037', '\x03'))
    blue = staticmethod(make_style('\x032', '\x03'))
    purple = staticmethod(make_style('\x036', '\x03'))
    grey = staticmethod(make_style('\x0315', '\x03'))


class CLIColors:
    bold = staticmethod(make_style('\033[1m', '\033[0m'))
    red = staticmethod(make_style('\033[31m', '\033[0m'))
    green = staticmethod(make_style('\033[32m', '\033[0m'))
    yellow = staticmethod(make_style('\033[33m', '\033[0m'))
    blue = staticmethod(make_style('\033[34m', '\033[0m'))
    purple = staticmethod(make_style('\033[35m', '\033[0m'))
    cyan = staticmethod(make_style('\033[36m', '\033[0m'))
    grey = staticmethod(make_style('\033[37m', '\033[0m'))
