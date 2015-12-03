from .helpers import public_api, twitter


def twitter_status(msg):
    url = 'statuses/show/{}.json'.format(msg.args[0])
    tweet = yield from twitter.request('GET', url)
    f = {'name': tweet['user']['screen_name'], 'text': tweet['text']}
    msg.reply("@{name}: «{text}»".format(**f))


def github(msg):
    url = "https://api.github.com/repos/{}/{}".format(*msg.args)
    repo = yield from public_api(url)
    fmt = "@{name} [{language}] ({stargazers_count}*): «{description}»"
    msg.reply(fmt.format(**repo))


def github_issue(msg):
    user, repo, kind, id = msg.args
    args = user, repo, id
    url = "https://api.github.com/repos/{}/{}/issues/{}".format(*args)
    issue = yield from public_api(url)
    issue['author'] = issue['user']['login']
    issue['labels'] = ' '.join('(%s)' % x['name'] for x in issue['labels'])
    fmt = "@{author} [#{number}]: «{title}» {labels}"
    msg.reply(fmt.format(**issue))


def reddit(msg):
    url = "https://api.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
    data = yield from public_api(url)
    post = data[0]['data']['children'][0]['data']
    fmt = "{author} ({upvote_ratio}+): «{title}» {url}"
    msg.reply(fmt.format(**post))


def hackernews(msg):
    url = "https://hacker-news.firebaseio.com/v0/item/"
    post = yield from public_api(url + "{}.json".format(msg.args[0]))
    fmt = "{by}: «{title}» {url}"
    msg.reply(fmt.format(**post))


def load(bot):
    github_repo = r'.*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)'
    bot.command(github_repo + r'/?(\s|$)')(github)
    bot.command(github_repo + r'/(issues|pull)/(\d+)')(github_issue)

    bot.command(r'.*https?://twitter.com/[^/]+/status/(\d+)')(twitter_status)
    bot.command(
        r'.*https?://www\.reddit\.com/r/([\w\d_\.-]+)/comments/([\w\d_\.-]+)')(
        reddit)
    bot.command(r'.*https?://news\.ycombinator\.com/item\?id=(\d+)')(hackernews)
