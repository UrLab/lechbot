from .helpers import public_api


def load(bot):
    @bot.command(r'.*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)/?(\s|$)')
    def github(msg):
        url = "https://api.github.com/repos/{}/{}".format(*msg.args[:2])
        repo = yield from public_api(url)
        fmt = "{name} ({language}) {stargazers_count}*: {description}"
        msg.reply(fmt.format(**repo))

    @bot.command(r'.*https?://(?:m\.)twitter.com/([^/]+)/status/(\d+)')
    def twitter(msg):
        msg.reply("Not implemented")

    @bot.command(r'https?://(?:www\.)reddit\.com/r/([\w\d_\.-]+)/comments/([\w\d_\.-]+)')
    def reddit(msg):
        url = "https://api.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
        data = yield from public_api(url)
        post = data[0]['data']['children'][0]['data']
        fmt = "{author} ({upvote_ratio}+): {title} {url}"
        msg.reply(fmt.format(**post))

    @bot.command(r'https?://news\.ycombinator\.com/item\?id=(\d+)')
    def hackernews(msg):
        url = "https://hacker-news.firebaseio.com/v0/item/"
        post = yield from public_api(url + "{}.json".format(msg.args[0]))
        fmt = "{by}: {title} {url}"
        msg.reply(fmt.format(**post))
