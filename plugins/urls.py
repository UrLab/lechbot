import html
import re
from datetime import datetime, timedelta

from ircbot.plugin import BotPlugin

from .helpers import public_api
from .komoot import KOMOOT_URL, describe_tour_summary, komoot_api
from .twitter import TwitterBasePlugin


class UrlShow(TwitterBasePlugin):
    """
    Post a preview for some well-known and frequent URLs
    """

    komoot_url = rf".*{KOMOOT_URL}"
    github_repo = r".*https?://github\.com/([\w\d_\.-]+)/([\w\d_\.-]+)"
    urlab_url = r".*https?://urlab\.be"

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

    @BotPlugin.command(
        r".*(?P<url>https://(\w+\.\w+)/(@\w+)?@\w+.\w+/(?P<toot_id>\d+))"
    )
    async def mastodon_toot(self, msg):
        url = f"https://mamot.fr/api/v1/statuses/{msg.kwargs['toot_id']}"
        response = await public_api(url)
        name = self.bot.text.bold("@", response["account"]["acct"])
        date = self.bot.text.grey(self.bot.naturaltime(response["created_at"]))
        text = html.unescape(re.sub("<[^<]+?>", "", response["content"]))

        msg.reply(f"{name} {date}: «{text}»")

    @BotPlugin.command(github_repo + r"/(issues|pull)/(\d+)(?:/\w+)?")
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

    @BotPlugin.command(github_repo + r"/commit/([0-9a-fA-F]{,40})")
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

    @BotPlugin.command(github_repo + r"/releases(?:/tag)/([^ ]+)")
    async def github_release(self, msg):
        url = "https://api.github.com/repos/{}/{}/releases/tags/{}".format(*msg.args)
        release = await public_api(url)
        name = self.bot.text.bold(release["name"])
        if release["draft"]:
            status = self.bot.text.red("ébauché")
        elif release["prerelease"]:
            status = self.bot.text.yellow("pré-publié")
        else:
            status = self.bot.text.green("publié")
        if release.get("published_at", None):
            release_date = self.bot.text.grey(
                self.bot.naturaltime(release["published_at"])
            )
        else:
            release_date = self.bot.text.grey(
                self.bot.naturaltime(release["created_at"])
            )
        author = release["author"]["login"]
        tag = self.bot.text.yellow(f"({release['tag_name']})")
        if len(release["assets"]):
            files = self.bot.text.blue(f"[{len(release['assets'])} fichiers]")
        else:
            files = ""
        msg.reply(f"«{name}» {tag} {status} {release_date} by @{author} {files}")

    @BotPlugin.command(github_repo)
    async def github_repo(self, msg):
        url = "https://api.github.com/repos/{}/{}".format(*msg.args)
        repo = await public_api(url)
        repo["name"] = self.bot.text.bold(repo["name"])
        repo["language"] = self.bot.text.purple("[", repo["language"], "]")
        repo["stars"] = self.bot.text.yellow("(", repo["stargazers_count"], "*)")
        fmt = "{name} {language} {stars}: «{description}»"
        msg.reply(fmt.format(**repo))

    @BotPlugin.command(r".*https?://gist\.github\.com/[^/]+/([0-9a-z]+)")
    async def github_gist(self, msg):
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
    )
    async def reddit(self, msg):
        url = "https://api.reddit.com/r/{}/comments/{}".format(*msg.args[:2])
        data = await public_api(url)
        post = data[0]["data"]["children"][0]["data"]
        post["author"] = self.bot.text.bold("@" + post["author"])
        post["upvote_ratio"] = self.bot.text.yellow("(", post["upvote_ratio"], "+)")
        post["url"] = self.bot.text.blue(post["url"])
        fmt = "{author} {upvote_ratio}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    @BotPlugin.command(r".*https?://news\.ycombinator\.com/item\?id=(\d+)")
    async def hackernews(self, msg):
        url = "https://hacker-news.firebaseio.com/v0/item/"
        post = await public_api(url + "{}.json".format(msg.args[0]))
        post["by"] = self.bot.text.bold("@", post["by"])
        post["url"] = self.bot.text.blue(post.get("url", ""))
        fmt = "{by}: «{title}» {url}"
        msg.reply(fmt.format(**post))

    # @BotPlugin.command(r'.*https?://(www\.)?youtube\.com/watch\?v=(\w+)')
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

    @BotPlugin.command(r".*https?://stackoverflow\.com\/questions\/(\d+)\/[^ /]+")
    async def stackoverflow(self, msg):
        await self.generic_stackexchange(msg, q_id=msg.args[0])

    @BotPlugin.command(
        r".*https?://([^\.]+)\.stackexchange\.com\/questions\/(\d+)\/[^ /]+"
    )
    async def stackexchange(self, msg):
        await self.generic_stackexchange(msg, q_id=msg.args[1], site=msg.args[0])

    @BotPlugin.command(urlab_url + r"/(projects/\d+)")
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

    @BotPlugin.command(urlab_url + r"/(events/\d+)")
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

    @BotPlugin.command(komoot_url + r"/highlight/(\d+)")
    async def komoot_highlight(self, msg):
        # Point: https://www.komoot.fr/highlight/753971
        # Segment: https://www.komoot.fr/highlight/2032270
        hl_id = msg.args[0]
        res = await komoot_api(f"/highlights/{hl_id}", auth=False)

        score = round(5 * res["score"])
        score_stars = score * self.bot.text.yellow("★") + (5 - score) * "★"
        name = self.bot.text.bold(res["name"])
        creator = res["_embedded"]["creator"]["display_name"]

        text = f"{name} {score_stars}"
        if res["type"] == "highlight_segment":
            text += self.bot.text.blue(
                f"{self.bot.naturalunits(res['distance'])}m "
                f"[⇗ {res['elevation_up']}m ⇘ {res['elevation_down']}m]"
            )
        text += f" (par @{creator})"

        msg.reply(text)

    @BotPlugin.command(komoot_url + r"/tour/(\d+)")
    async def komoot_tour(self, msg):
        # Done: https://www.komoot.fr/tour/229408387
        # Planned: https://www.komoot.fr/tour/226867974
        tour_id = msg.args[0]
        res = await komoot_api(f"/tours/{tour_id}")

        if res.get("error") == "AccessDenied":
            return msg.reply("Ce tour est privé")

        name = self.bot.text.bold(res["name"])
        create_time = self.bot.text.grey(self.bot.naturaltime(res["date"]))

        if res["type"] == "tour_planned":
            duration = timedelta(seconds=res["duration"])
        else:
            duration = timedelta(seconds=res["time_in_motion"])
        if duration < timedelta(hours=10):
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() // 60) % 60)
            tour_time = f"{hours}h{minutes:02}"
        else:
            tour_time = self.bot.naturaltime(duration)

        if res["type"] == "tour_planned":
            tour_type = self.bot.text.yellow("planifié")
            tour_time = "~" + tour_time
        else:
            tour_type = self.bot.text.green("effectué")
        distance = self.bot.text.blue(
            f"{self.bot.naturalunits(res['distance'])}m "
            f"[⇗ {int(res['elevation_up'])}m ⇘ {int(res['elevation_down'])}m]"
        )
        creator = res["_embedded"]["creator"]["display_name"]

        text = f"{name}: {tour_time}, {distance} ({tour_type} {create_time} par @{creator})"
        if "summary" in res:
            text += "\n" + describe_tour_summary(res["summary"])

        msg.reply(text)
