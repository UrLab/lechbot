from .helpers import public_api, twitter
from config import INCUBATOR


def twitter_status(msg):
        url = 'statuses/show/{}.json'.format(msg.args[0])
        tweet = yield from twitter.request('GET', url)
        f = {
            'name': msg.bot.text.bold('@', tweet['user']['screen_name']),
            'text': tweet['text']
        }
        msg.reply("{name}: «{text}»".format(**f))


def load(bot):
    github_repo = r'.*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)'

    bot.command(r'.*https?://twitter.com/[^/]+/status/(\d+)')(twitter_status)

    @bot.command(github_repo + r'/?(\s|$)')
    def github(msg):
        url = "https://api.github.com/repos/{}/{}".format(*msg.args)
        repo = yield from public_api(url)
        repo['name'] = bot.text.bold(repo['name'])
        repo['language'] = bot.text.purple('[', repo['language'], ']')
        repo['stars'] = bot.text.yellow('(', repo['stargazers_count'], '*)')
        fmt = "{name} {language} {stars}: «{description}»"
        msg.reply(fmt.format(**repo))

    @bot.command(github_repo + r'/(issues|pull)/(\d+)')
    def github_issue(msg):
        user, repo, kind, id = msg.args
        args = user, repo, id
        url = "https://api.github.com/repos/{}/{}/issues/{}".format(*args)
        issue = yield from public_api(url)
        issue['author'] = bot.text.bold('@' + issue['user']['login'])
        issue['labels'] = ' '.join(bot.text.grey('(%s)') % x['name'] for x in issue['labels'])
        if issue['state'] == 'open':
            issue['number'] = bot.text.green('[#', issue['number'], ' (open)]')
        elif issue['state'] == 'closed':
            issue['number'] = bot.text.red('[#', issue['number'], ' (closed)]')
        fmt = "{author} {number}: «{title}» {labels}"
        msg.reply(fmt.format(**issue))

    @bot.command(r'.*https?://www\.reddit\.com/r/([\w\d_\.-]+)/comments/([\w\d_\.-]+)')
    def reddit(msg):
        url = "https://api.bot.text.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
        data = yield from public_api(url)
        post = data[0]['data']['children'][0]['data']
        post['author'] = bot.text.bold('@' + post['author'])
        post['upvote_ratio'] = bot.text.yellow('(', post['upvote_ratio'], '+)')
        post['url'] = bot.text.blue(post['url'])
        fmt = "{author} {upvote_ratio}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @bot.command(r'.*https?://news\.ycombinator\.com/item\?id=(\d+)')
    def hackernews(msg):
        url = "https://hacker-news.firebaseio.com/v0/item/"
        post = yield from public_api(url + "{}.json".format(msg.args[0]))
        post['by'] = bot.text.bold('@', post['by'])
        post['url'] = bot.text.blue(post['url'])
        fmt = "{by}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @bot.command(r'.*https?://urlab\.be(/projects/\d+)')
    def urlab_project(msg):
        proj = yield from public_api(msg.args[0])
        if proj['status'] == 'f':    # Finished
            color = bot.text.green
        elif proj['status'] == "p":  # Proposition
            color = bot.text.yellow
        elif proj['status'] == "i":  # In progress
            color = bot.text.blue
        else:                        # Unknown status
            color = bot.text.grey

        proj['desc'] = color(proj['short_description'])
        proj['title'] = bot.text.bold(proj['title'])
        fmt = "{title}: {desc}"
        msg.reply(fmt.format(**proj))

    PROJECT_STATUS = {
        'p': bot.text.yellow,  # Proposition
        'i': bot.text.blue,    # In progress
        'f': bot.text.green,   # Finished
    }

    @bot.command(INCUBATOR + r'(projects/\d+)')
    def urlab_project(msg):
        proj = yield from public_api(msg.args[0])
        color = PROJECT_STATUS.get(proj['status'], bot.text.grey)
        proj['desc'] = color(proj['short_description'])
        proj['title'] = bot.text.bold(proj['title'])
        fmt = "{title}: {desc}"
        msg.reply(fmt.format(**proj))

    EVENT_STATUS = {
        'r': bot.text.bold,
        'i': bot.text.yellow,
    }

    @bot.command(INCUBATOR + r'(events/\d+)')
    def urlab_event(msg):
        evt = yield from public_api(msg.args[0])
        evt['when'] = bot.text.yellow(bot.naturaltime(evt['start']))
        color = EVENT_STATUS.get(evt['status'], bot.text.grey)
        evt['title'] = color(evt['title'])
        evt['place'] = bot.text.purple(evt['place'])
        fmt = "{title} ({when} :: {place})"
        msg.reply(fmt.format(**evt))
