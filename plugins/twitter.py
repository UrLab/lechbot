def load(bot):
    @bot.command(r'\!twitter +([^ ].+)')
    def tweet_message(msg):
        """Tweete avec le compte de UrLab (@urlabbxl)"""
        text = msg.args[0]
        msg.reply("Not implemented")
        bot.log.info('Tweet "' + text + '" by ' + msg.user.nick)

    @bot.command(r'\!retweet https?://.*twitter.com/([^/]+)/status/(\d+)')
    def retweet_message(msg):
        """Retweete un message avec le compte de UrLab (@urlabbxl)"""
        user, status = msg.args
        msg.reply("Not implemented")
        bot.log.info('Retweet @' + user + ' by ' + msg.user.nick)
