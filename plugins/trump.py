import json
import random
from datetime import date

from ircbot.plugin import BotPlugin

n = 3


def compute_cumsum(xs):
    cur = 0
    ret = []
    for x in xs:
        ret.append(cur + x)
        cur += x
    return ret


def random_choice(choices, probas):
    cumsum = compute_cumsum(probas)
    r = random.random()
    probas_f = [r >= x for x in cumsum]
    choice = 0
    for i, p in enumerate(probas_f):
        if not p:
            choice = i
            break
    return choices[choice]


def generate_sentence(probas):
    prev = ["$BEGINNING" for _ in range(n)]
    w = ""
    s = ""
    while True:
        if w == "POINT":
            break
        x = probas[tuple(prev)]
        w = random_choice(list(x.keys()), list(x.values()))
        if w in ["POINT", "VIRGULE", "P-V", "EXCLAMATION"]:
            s += " " + w + " "
        elif w == "$NUMBER":
            s += " " + str(random.randint(0, 100))
        else:
            s += " " + w
        prev = [prev[i + 1] for i in range(len(prev) - 1)] + [w]
    s = s.replace(" POINT ", ".")
    s = s.replace(" VIRGULE  ", ",")
    s = s.replace(" P-V ", ";")
    s = s.replace(" EXCLAMATION ", "!")
    return s.strip()


def read_json():
    try:
        with open("data/trump_data.json", "r") as f:
            probas = json.load(f)
        probas = {
            tuple([x.strip()[1:][:-1] for x in k[1:][:-1].split(",")]): v
            for k, v in probas.items()
        }
        return probas
    except FileNotFoundError:
        return False


class Trump(BotPlugin):
    probas = read_json()

    @BotPlugin.command(r"\!trump$")
    def train(self, msg):
        if date.today().day == 7 and date.today().month == 11:
            msg.reply(
                random.choice(
                    [
                        "I WON THIS ELECTION, BY A LOT!",
                        "THE OBSERVERS WERE NOT ALLOWED INTO THE COUNTING ROOMS. I WON THE ELECTION, GOT 71,000,000 LEGAL VOTES. BAD THINGS HAPPENED WHICH OUR OBSERVERS WERE NOT ALLOWED TO SEE. NEVER HAPPENED BEFORE. MILLIONS OF MAIL-IN BALLOTS WERE SENT TO PEOPLE WHO NEVER ASKED FOR THEM!",
                        "71,000,000 Legal Votes. The most EVER for a sitting President!",
                    ]
                )
            )
        elif self.probas:
            try:
                s = generate_sentence(self.probas)
                msg.reply(s)
            except:
                msg.reply("I failed because I'm badly written (this is not Trump btw)")
        else:
            msg.reply("The data file is missing (this is not Trump btw)")
