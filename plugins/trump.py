from ircbot.plugin import BotPlugin
import json
import random
import numpy as np

n = 3


def generate_sentence(probas):
    prev = ["$BEGINNING" for _ in range(n)]
    w = ""
    s = ""
    while True:
        if w == "POINT":
            break
        x = probas[tuple(prev)]
        w = np.random.choice(list(x.keys()), p=list(x.values()))
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
    with open("data/trump_data.json", "r") as f:
        probas = json.load(f)
    probas = {tuple([x.strip()[1:][:-1] for x in k[1:][:-1].split(",")]): v for k, v in probas.items()}
    return probas


class Trump(BotPlugin):
    def __init__(self):
        super()
        try:
            self.probas = read_json()
        except FileNotFoundError:
            self.probas = False

    @BotPlugin.command(r'\!trump$')
    def train(self, msg):
        if self.probas:
            try:
                s = generate_sentence(self.probas)
                msg.reply(s)
            except:
                msg.reply("I failed because I'm badly written (this is not Trump btw)")
        else:
            msg.reply("The data file is missing (this is not Trump btw)")
