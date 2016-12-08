import json
import asyncio
from aioauth_client import TwitterClient
from ircbot.plugin import BotPlugin
from operator import itemgetter


class TwitterBasePlugin(BotPlugin):
    """
    Common base for Twitter plugins
    """
    REQUIRED_CREDENTIALS = [
        'consumer_key', 'consumer_secret',
        'oauth_token', 'oauth_token_secret'
    ]

    def __init__(self, credentials):
        for key in self.REQUIRED_CREDENTIALS:
            if key not in credentials:
                raise ValueError("Twitter {key} is mandatory".format(key=key))
        self.twitter = TwitterClient(**credentials)

    def twitter_request(self, *args, **kwargs):
        response = yield from self.twitter.request(*args, **kwargs)
        res = yield from response.json()
        yield from response.release()
        return res

    def format_tweet(self, tweet):
        entities = tweet.get('entities', {}).get('urls', [])
        entities += tweet.get('entities', {}).get('media', [])
        urls = [x['expanded_url'] for x in entities]
        url_lines = '\n'.join(' -> ' + self.bot.text.blue(u) for u in urls)
        f = {
            'name': self.bot.text.bold('@', tweet['user']['screen_name']),
            'text': tweet['text'],
            'urls': url_lines,
        }
        return "{name}: «{text}»\n{urls}".format(**f)


class Twitter(TwitterBasePlugin):
    """
    Plugin to emit messages to Twitter
    """

    @BotPlugin.command(r'\!twitter +([^ ].+)')
    def tweet_message(self, msg):
        """Tweete un message"""
        text = msg.args[0]
        yield from self.twitter_request('POST', 'statuses/update.json',
                                        params={'status': text})
        msg.reply("Pinky pinky !", hilight=True)
        self.bot.log.info('Tweet "' + text + '" by ' + msg.user)

    @BotPlugin.command(r'\!retweet https?://.*twitter.com/[^/]+/status/(\d+)')
    def retweet_message(self, msg):
        """Retweete un message"""
        tweet_id = msg.args[0]
        url = 'statuses/retweet/{}.json'.format(tweet_id)
        yield from self.twitter_request('POST', url)
        url = 'statuses/show/{}.json'.format(msg.args[0])
        tweet = yield from self.twitter_request('GET', url)
        msg.reply("Retweeté \\\\o< " + self.format_tweet(tweet), hilight=True)


class TwitterStream(TwitterBasePlugin):
    """
    Twitter plugin to follow a Twitter livestream
    """
    def __init__(self, credentials, follow_name):
        super(TwitterStream, self).__init__(credentials)
        self.follow_name = follow_name

    def _is_mentioned(self, mention):
        return self.follow_name == mention['screen_name']

    def handle_event(self, evt):
        self.bot.log.debug("Handle " + repr(evt))
        if 'event' in evt:
            if evt['event'] == 'favorite':
                f = {
                    'tweet': self.format_tweet(evt['target_object']),
                    'sender': self.bot.text.blue('@' + evt['source']['screen_name']),
                    'like': self.bot.text.red('<3')
                }
                self.say("{sender} {like} {tweet}".format(**f))
        elif 'entities' in evt:
            mentions = list(
                filter(self._is_mentioned, evt['entities']['user_mentions']))
            if mentions:
                self.say(self.format_tweet(evt))

    @asyncio.coroutine
    def read_stream(self, url, callback):
        resp = yield from self.twitter.request('GET', url, headers={
            'User-Agent': "LechBot"
        })
        if resp.status != 200:
            r = yield from resp.read()
            resp.close()
            raise Exception(r)
        self.bot.log.info("Connected to Twitter stream " + url)
        while True:
            line = ''
            while not line.endswith('\r\n'):
                char = yield from resp.content.read(1)
                if not char:
                    resp.close()
                    return
                line += char.decode()
            line = line.strip()
            if line:
                try:
                    callback(json.loads(line))
                except:
                    self.bot.log.exception("Error when handling Twitter stream item")

    @BotPlugin.on_connect
    def startup(self):
        while True:
            yield from self.read_stream(
                'https://userstream.twitter.com/1.1/user.json',
                self.handle_event)
