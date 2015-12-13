from .helpers import public_api
from .twitter import TwitterBasePlugin
from ircbot.plugin import BotPlugin


class UrlShow(TwitterBasePlugin):
    github_repo = r'.*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)'
    urlab_url = r'.*https?://urlab\.be'

    @BotPlugin.command(r'.*https?://twitter.com/[^/]+/status/(\d+)')
    def twitter_status(self, msg):
        url = 'statuses/show/{}.json'.format(msg.args[0])
        tweet = yield from self.twitter_request('GET', url)
        msg.reply(self.format_tweet(tweet))

    @BotPlugin.command(github_repo + r'/?(\s|$)')
    def github(self, msg):
        url = "https://api.github.com/repos/{}/{}".format(*msg.args)
        repo = yield from public_api(url)
        repo['name'] = self.bot.text.bold(repo['name'])
        repo['language'] = self.bot.text.purple('[', repo['language'], ']')
        repo['stars'] = self.bot.text.yellow('(', repo['stargazers_count'], '*)')
        fmt = "{name} {language} {stars}: «{description}»"
        msg.reply(fmt.format(**repo))

    @BotPlugin.command(github_repo + r'/(issues|pull)/(\d+)')
    def github_issue(self, msg):
        user, repo, kind, id = msg.args
        args = user, repo, id
        url = "https://api.github.com/repos/{}/{}/issues/{}".format(*args)
        issue = yield from public_api(url)
        issue['author'] = self.bot.text.bold('@' + issue['user']['login'])
        issue['labels'] = ' '.join(self.bot.text.grey('(%s)') % x['name'] for x in issue['labels'])
        if issue['state'] == 'open':
            issue['number'] = self.bot.text.green('[#', issue['number'], ' (open)]')
        elif issue['state'] == 'closed':
            issue['number'] = self.bot.text.red('[#', issue['number'], ' (closed)]')
        fmt = "{author} {number}: «{title}» {labels}"
        msg.reply(fmt.format(**issue))

    @BotPlugin.command(github_repo + r'/commit/([0-9a-fA-F]{,40})')
    def github_commit(self, msg):
        url = "https://api.github.com/repos/{}/{}/commits/{}".format(*msg.args)
        commit = yield from public_api(url)
        commit['author'] = self.bot.text.bold('@' + commit['author']['login'])
        commit['title'] = commit['commit']['message']
        additions = self.bot.text.green("%d+" % commit['stats']['additions'])
        deletions = self.bot.text.red("%d-" % commit['stats']['deletions'])
        files_changed = self.bot.text.yellow("%d files" % len(commit['files']))
        commit['stats'] = " ".join([additions, deletions, files_changed])
        msg.reply("{author} «{title}» ({stats})".format(**commit))

    @BotPlugin.command(r'.*https?://www\.reddit\.com/r/([\w\d_\.-]+)/comments/([\w\d_\.-]+)')
    def reddit(self, msg):
        url = "https://api.bot.text.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
        data = yield from public_api(url)
        post = data[0]['data']['children'][0]['data']
        post['author'] = self.bot.text.bold('@' + post['author'])
        post['upvote_ratio'] = self.bot.text.yellow('(', post['upvote_ratio'], '+)')
        post['url'] = self.bot.text.blue(post['url'])
        fmt = "{author} {upvote_ratio}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @BotPlugin.command(r'.*https?://news\.ycombinator\.com/item\?id=(\d+)')
    def hackernews(self, msg):
        url = "https://hacker-news.firebaseio.com/v0/item/"
        post = yield from public_api(url + "{}.json".format(msg.args[0]))
        post['by'] = self.bot.text.bold('@', post['by'])
        post['url'] = self.bot.text.blue(post['url'])
        fmt = "{by}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @BotPlugin.command(urlab_url + r'/(projects/\d+)')
    def urlab_project(self, msg):
        project_status = {
            'p': self.bot.text.yellow,  # Proposition
            'i': self.bot.text.blue,    # In progress
            'f': self.bot.text.green,   # Finished
        }

        proj = yield from public_api(msg.args[0])
        color = project_status.get(proj['status'], self.bot.text.grey)
        proj['desc'] = color(proj['short_description'])
        proj['title'] = self.bot.text.bold(proj['title'])
        fmt = "{title}: {desc}"
        msg.reply(fmt.format(**proj))

    @BotPlugin.command(urlab_url + r'/(events/\d+)')
    def urlab_event(self, msg):
        event_status = {
            'r': self.bot.text.bold,    # Ready
            'i': self.bot.text.yellow,  # Incubation
        }

        evt = yield from public_api(msg.args[0])
        if evt.get('start', None):
            evt['when'] = self.bot.text.yellow(self.bot.naturaltime(evt['start']))
        else:
            evt['when'] = "pas de date"
        color = event_status.get(evt['status'], self.bot.text.grey)
        evt['title'] = color(evt['title'])
        evt['place'] = self.bot.text.purple(evt['place'])
        fmt = "{title} ({when} :: {place})"
        msg.reply(fmt.format(**evt))
