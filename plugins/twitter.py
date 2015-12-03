from .helpers import twitter
from .urls import twitter_status


def load(bot):
    @bot.command(r'\!twitter +([^ ].+)')
    def tweet_message(msg):
        """Tweete avec le compte de UrLab (@urlabbxl)"""
        text = msg.args[0]
        res = yield from twitter.request('POST', 'statuses/update.json',
                                         params={'status': text})
        msg.reply("Pinky pinky !", hilight=True)
        bot.log.info('Tweet "' + text + '" by ' + msg.user.nick)

    @bot.command(r'\!retweet https?://.*twitter.com/[^/]+/status/(\d+)')
    def retweet_message(msg):
        """Retweete un message avec le compte de UrLab (@urlabbxl)"""
        tweet_id = msg.args[0]
        url = 'statuses/retweet/{}.json'.format(tweet_id)
        yield from twitter.request('POST', url)
        yield from twitter_status(msg)
        msg.reply("Retweeté \\\\o<", hilight=True)
