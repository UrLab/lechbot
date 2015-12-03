def make_style(before, after='\x0F'):
    if after is None:
        after = before

    def inner(*args):
        text = ''.join(map(str, args))
        if text[0].isdigit():
            text = ' ' + text
        return '{}{}{}'.format(before, text, after)
    return inner

bold = make_style('\x02', '\x02')
red = make_style('\x035', '\x03')
green = make_style('\x033', '\x03')
yellow = make_style('\x038', '\x03')
blue = make_style('\x0312', '\x03')
purple = make_style('\x036', '\x03')
grey = make_style('\x0315', '\x03')
