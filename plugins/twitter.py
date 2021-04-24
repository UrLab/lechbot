from aioauth_client import TwitterClient

from ircbot.plugin import BotPlugin


class TwitterBasePlugin(BotPlugin):
    """
    Common base for Twitter plugins
    """

    REQUIRED_CREDENTIALS = [
        "consumer_key",
        "consumer_secret",
        "oauth_token",
        "oauth_token_secret",
    ]

    def __init__(self, credentials):
        for key in self.REQUIRED_CREDENTIALS:
            if key not in credentials:
                raise ValueError("Twitter {key} is mandatory".format(key=key))
        self.twitter = TwitterClient(**credentials)

    async def twitter_request(self, *args, **kwargs):
        res = await self.twitter.request(*args, **kwargs)
        return res

    def format_tweet(self, tweet):
        entities = tweet.get("entities", {}).get("urls", [])
        entities += tweet.get("entities", {}).get("media", [])
        urls = [x["expanded_url"] for x in entities]
        url_lines = "\n".join(" -> " + self.bot.text.blue(u) for u in urls)
        f = {
            "name": self.bot.text.bold("@", tweet["user"]["screen_name"]),
            "text": tweet["full_text"] if "full_text" in tweet else tweet["text"],
            "urls": url_lines,
        }
        return "{name}: «{text}»\n{urls}".format(**f)


class Twitter(TwitterBasePlugin):
    """
    Plugin to emit messages to Twitter
    """

    @BotPlugin.command(r"\!twitter +([^ ].+)")
    async def tweet_message(self, msg):
        """Tweete un message"""
        text = msg.args[0]
        await self.twitter_request(
            "POST", "statuses/update.json", params={"status": text}
        )
        msg.reply("Pinky pinky !", hilight=True)
        self.bot.log.info('Tweet "' + text + '" by ' + msg.user)

    @BotPlugin.command(r"\!retweet https?://.*twitter.com/[^/]+/status/(\d+)")
    async def retweet_message(self, msg):
        """Retweete un message"""
        tweet_id = msg.args[0]
        url = "statuses/retweet/{}.json".format(tweet_id)
        await self.twitter_request("POST", url)
        url = "statuses/show/{}.json".format(msg.args[0])
        tweet = await self.twitter_request("GET", url)
        msg.reply("Retweeté \\\\o< " + self.format_tweet(tweet), hilight=True)
