import json
from ircbot.plugin import BotPlugin


class Sudo(BotPlugin):
    @BotPlugin.command(r"sudo .*")
    async def sudo(self, msg):
        """passe la command en mode sudo"""
        
        with open("data/sudoers.json", "r") as file: # reads the file each time its called, not optimal
            data = json.load(file)  
        
        if msg.user in data["users"]: # could use a dict intead of a list for faster lookup
            self.bot.feed(msg.user, msg.chan, msg.text[5:], sudo=True) # strip the 'sudo ' part of the command and feed it back to the bot
        else:
            msg.reply(msg.user + " is not a sudoer")


    @BotPlugin.command(r"\!usermod -aG sudo ([^\s]*)")
    async def add_sudoer(self, msg):
        """ajoute le nom d'utilisateur a la liste de sudoer"""
        
        with open("data/sudoers.json", "r") as file: # reads the file each time its called, not optimal
            data = json.load(file)
        
        target_user = msg.args[0]
        data["users"].append(target_user)
        
        with open("data/sudoers.json", "w") as file:
            json.dump(data, file)

        msg.reply(target_user + " added to sudoers")
        