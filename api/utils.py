import random
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import requests
import tweepy

YESTERDAY = datetime.now().astimezone() - timedelta(days=1)


class InvidiousAPI:
    def __init__(self, domain):
        self.domain = domain
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
        }
        self.jp50 = [c for c in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"]

        random.shuffle(self.jp50)

    def _json(self, path):
        url = "https://" + self.domain + path
        print(f"Downloading JSON from {url}")
        return requests.get(url, headers=self.headers).json()

    def stats(self):
        return self._json("/api/v1/stats")

    def today_videos(self):
        return self._json("/api/v1/search?q=" + quote_plus(" OR ".join(self.jp50)) + "&date=today&sort_by=view_count")

    def today_lives(self):
        return self._json("/api/v1/search?q=" + quote_plus(" OR ".join(self.jp50)) + "&date=today&sort_by=view_count&features=live")


class TwitterAPI:
    def __init__(self, consumer_key="3nVuSoBZnx6U4vzUxf5w", consumer_secret="Bcs59EFbbsdF6Sl9Ng71smgStWEGwXXKSjYvPVt7qys"):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(auth)

    def today_tweets(self):
        return [status._json for status in self.api.search("min_faves:10000", lang="ja", result_type="mixed", count=40, since=YESTERDAY.date().isoformat())]
