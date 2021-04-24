from datetime import datetime

from ircbot.plugin import BotPlugin

from .helpers import public_api
from .twitter import TwitterBasePlugin


class UrlShow(TwitterBasePlugin):
    """
    Post a preview for some well-known and frequent URLs
    """

    github_repo = r".*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)"
    urlab_url = r".*https?://urlab\.be"
    end_url = r"(?:$|\s|\)|\]|\})"

    def check_mark(self, ok=True):
        res = self.bot.text.green("✓") if ok else self.bot.text.red("✗")
        return self.bot.text.bold(res)

    @BotPlugin.command(r".*https?://(?:mobile\.)?twitter.com/[^/]+/status/(\d+)")
    async def twitter_status(self, msg):
        url = "statuses/show/{}.json".format(msg.args[0])
        tweet = await self.twitter_request(
            "GET", url, params={"tweet_mode": "extended"}
        )
        msg.reply(self.format_tweet(tweet))

    @BotPlugin.command(github_repo + r"/?(\s|$)" + end_url)
    async def github(self, msg):
        url = "https://api.github.com/repos/{}/{}".format(*msg.args)
        repo = await public_api(url)
        repo["name"] = self.bot.text.bold(repo["name"])
        repo["language"] = self.bot.text.purple("[", repo["language"], "]")
        repo["stars"] = self.bot.text.yellow("(", repo["stargazers_count"], "*)")
        fmt = "{name} {language} {stars}: «{description}»"
        msg.reply(fmt.format(**repo))

    @BotPlugin.command(github_repo + r"/(issues|pull)/(\d+)" + end_url)
    async def github_issue(self, msg):
        user, repo, kind, id = msg.args
        args = user, repo, id
        url = "https://api.github.com/repos/{}/{}/issues/{}".format(*args)
        issue = await public_api(url)
        issue["when"] = self.bot.text.grey(self.bot.naturaltime(issue["created_at"]))
        issue["author"] = self.bot.text.bold("@" + issue["user"]["login"])
        issue["labels"] = " ".join(
            self.bot.text.grey("(%s)") % x["name"] for x in issue["labels"]
        )
        if issue["state"] == "open":
            issue["number"] = self.bot.text.green("[#", issue["number"], " (open)]")
        elif issue["state"] == "closed":
            issue["number"] = self.bot.text.red("[#", issue["number"], " (closed)]")
        fmt = "{author} {when} {number}: «{title}» {labels}"
        msg.reply(fmt.format(**issue))

    @BotPlugin.command(github_repo + r"/commit/([0-9a-fA-F]{,40})" + end_url)
    async def github_commit(self, msg):
        url = "https://api.github.com/repos/{}/{}/commits/{}".format(*msg.args)
        commit = await public_api(url)
        additions = self.bot.text.green("%d+" % commit["stats"]["additions"])
        deletions = self.bot.text.red("%d-" % commit["stats"]["deletions"])
        files_changed = self.bot.text.yellow("%d fichiers" % len(commit["files"]))
        f = {
            "author": self.bot.text.bold("@" + commit["author"]["login"]),
            "title": commit["commit"]["message"],
            "stats": " ".join([additions, deletions, files_changed]),
            "when": self.bot.text.grey(
                self.bot.naturaltime(commit["commit"]["author"]["date"])
            ),
        }
        msg.reply("{author} {when} «{title}» ({stats})".format(**f))

    @BotPlugin.command(r".*https?://gist\.github\.com/[^/]+/([0-9a-z]+)" + end_url)
    async def gist(self, msg):
        url = "https://api.github.com/gists/{}".format(msg.args[0])
        gist = await public_api(url)
        filelist = ", ".join(i["filename"] for i in gist["files"].values())
        f = {
            "author": self.bot.text.bold("@" + gist["owner"]["login"]),
            "when": self.bot.text.grey(self.bot.naturaltime(gist["updated_at"])),
            "title": gist["description"],
            "files": self.bot.text.yellow(filelist),
        }
        msg.reply("{author} {when} «{title}» ({files})".format(**f))

    @BotPlugin.command(
        r".*https?://www\.reddit\.com/r/([\w\d_\.-]+)/comments/([\w\d_\.-]+)/([\w\d_\.-]+)/"
        + end_url
    )
    async def reddit(self, msg):
        url = "https://api.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
        data = await public_api(url, verify_ssl=False)
        post = data[0]["data"]["children"][0]["data"]
        post["author"] = self.bot.text.bold("@" + post["author"])
        post["upvote_ratio"] = self.bot.text.yellow("(", post["upvote_ratio"], "+)")
        post["url"] = self.bot.text.blue(post["url"])
        fmt = "{author} {upvote_ratio}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @BotPlugin.command(r".*https?://news\.ycombinator\.com/item\?id=(\d+)" + end_url)
    async def hackernews(self, msg):
        url = "https://hacker-news.firebaseio.com/v0/item/"
        post = await public_api(url + "{}.json".format(msg.args[0]))
        post["by"] = self.bot.text.bold("@", post["by"])
        post["url"] = self.bot.text.blue(post.get("url", ""))
        fmt = "{by}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    # @BotPlugin.command(r'.*https?://(www\.)?youtube\.com/watch\?v=(\w+)' + end_url)
    # def youtube(self, msg):
    #     # Not available atm because of API restrictions
    #     pass

    async def generic_stackexchange(self, msg, q_id, site="stackoverflow"):
        url = "https://api.stackexchange.com/2.2/questions/{}?&site={}"
        post = await public_api(url.format(q_id, site))
        for q in post.get("items", []):
            if q["score"] >= 0:
                score = self.bot.text.green("+%d" % q["score"])
            else:
                score = self.bot.text.red("%d" % q["score"])
            ctx = {
                "date": self.bot.naturaltime(
                    datetime.fromtimestamp(q["creation_date"])
                ),
                "title": self.bot.text.bold(q["title"]),
                "tags": " ".join(
                    self.bot.text.purple("(" + t + ")") for t in q["tags"]
                ),
                "url": self.bot.text.blue(q["link"]),
                "solved": self.check_mark(q["is_answered"]),
                "score": score,
            }
            fmt = "«{title}» [{solved} {score}] ({date}) {tags}\n -> {url}"
            msg.reply(fmt.format(**ctx))

    @BotPlugin.command(
        r".*https?://stackoverflow\.com\/questions\/(\d+)\/[^ /]+" + end_url
    )
    async def stackoverflow(self, msg):
        await self.generic_stackexchange(msg, q_id=msg.args[0])

    @BotPlugin.command(
        r".*https?://([^\.]+)\.stackexchange\.com\/questions\/(\d+)\/[^ /]+" + end_url
    )
    async def stackexchange(self, msg):
        await self.generic_stackexchange(msg, q_id=msg.args[1], site=msg.args[0])

    @BotPlugin.command(urlab_url + r"/(projects/\d+)" + end_url)
    async def urlab_project(self, msg):
        project_status = {
            "p": self.bot.text.yellow,  # Proposition
            "i": self.bot.text.blue,  # In progress
            "f": self.bot.text.green,  # Finished
        }

        proj = await public_api(msg.args[0])
        color = project_status.get(proj["status"], self.bot.text.grey)
        proj["desc"] = color(proj["short_description"])
        proj["title"] = self.bot.text.bold(proj["title"])
        fmt = "{title}: {desc}"
        msg.reply(fmt.format(**proj))

    @BotPlugin.command(urlab_url + r"/(events/\d+)" + end_url)
    async def urlab_event(self, msg):
        event_status = {
            "r": self.bot.text.bold,  # Ready
            "i": self.bot.text.yellow,  # Incubation
        }

        evt = await public_api(msg.args[0])
        if evt.get("start", None):
            evt["when"] = self.bot.text.yellow(self.bot.naturaltime(evt["start"]))
        else:
            evt["when"] = "pas de date"
        color = event_status.get(evt["status"], self.bot.text.grey)
        evt["title"] = color(evt["title"])
        evt["place"] = self.bot.text.purple(evt["place"])
        fmt = "{title} ({when} :: {place})"
        msg.reply(fmt.format(**evt))
