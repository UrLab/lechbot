import json
from datetime import date, timedelta

import roman

from ircbot.plugin import BotPlugin

days = json.load(open("plugins/les_republicains_days.json"))
months = json.load(open("plugins/les_republicains_months.json"))


class LesRepublicains(BotPlugin):
    @BotPlugin.command(r"\!les_republicains")
    def les_republicains(self, msg):
        today = date.today()
        # find the current month in republican calendar
        current_republican_month = ""
        for month, bounds in months.items():
            start = date(today.year, bounds[1], bounds[0])
            end = date(today.year, bounds[3], bounds[2])
            if start <= today <= end:
                current_republican_month = month
                current_month_start = start
                break
        # list the days of the current month until we find the right one
        date_republican = current_month_start
        current_republican_day = ""
        for day, day_name in enumerate(days.get(current_republican_month, [])):
            if date_republican == today:
                current_republican_day = day_name
                break
            date_republican += timedelta(days=1)
        # compute the year
        if today >= date(
            today.year, 9, 22
        ):  # republican calendar starts on 22th september 1792
            current_republican_year = today.year - 1791
        else:
            current_republican_year = today.year - 1792
        msg.reply(
            "Nous sommes le {} {} an {} ({})".format(
                day + 1,  # days start on 1
                current_republican_month,
                roman.toRoman(current_republican_year),
                current_republican_day,  # day name
            )
        )
