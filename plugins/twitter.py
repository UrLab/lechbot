from aioauth_client import TwitterClient
from ircbot.plugin import BotPlugin


class TwitterBasePlugin(BotPlugin):
    REQUIRED_CREDENTIALS = [
        'consumer_key', 'consumer_secret',
        'oauth_token', 'oauth_token_secret'
    ]

    def __init__(self, credentials):
        for key in self.REQUIRED_CREDENTIALS:
            if key not in credentials:
                raise ValueError("{key} is mandatory".format(key=key))
        self.twitter = TwitterClient(**credentials)

    def twitter_request(self, *args, **kwargs):
        response = yield from self.twitter.request(*args, **kwargs)
        res = yield from response.json()
        yield from response.release()
        return res

    def format_tweet(self, tweet):
        f = {
            'name': self.bot.text.bold('@', tweet['user']['screen_name']),
            'text': tweet['text']
        }
        return "{name}: «{text}»".format(**f)


class Twitter(TwitterBasePlugin):
    @BotPlugin.command(r'\!twitter +([^ ].+)')
    def tweet_message(self, msg):
        """Tweete un message"""
        text = msg.args[0]
        yield from self.twitter_request('POST', 'statuses/update.json',
                                        params={'status': text})
        msg.reply("Pinky pinky !", hilight=True)
        self.bot.log.info('Tweet "' + text + '" by ' + msg.user.nick)

    @BotPlugin.command(r'\!retweet https?://.*twitter.com/[^/]+/status/(\d+)')
    def retweet_message(self, msg):
        """Retweete un message"""
        tweet_id = msg.args[0]
        url = 'statuses/retweet/{}.json'.format(tweet_id)
        yield from self.twitter_request('POST', url)
        url = 'statuses/show/{}.json'.format(msg.args[0])
        tweet = yield from self.twitter_request('GET', url)
        msg.reply("Retweeté \\\\o<" + self.format_tweet(tweet), hilight=True)
