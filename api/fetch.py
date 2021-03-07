from pathlib import Path
from pprint import pprint
from urllib.parse import quote_plus

import feedparser
import pandas as pd
import requests

jp50 = [c for c in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"]
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"}

pprint(requests.get("https://invidious.snopyta.org/api/v1/stats", headers=headers).json())

youtube_video = requests.get("https://invidious.snopyta.org/api/v1/search?q=" + quote_plus(" OR ".join(jp50)) + "&date=today", headers=headers).json()
youtube_video_df = pd.DataFrame(
    map(
        lambda video: {
            "url": "https://www.youtube.com/watch?v=" + video["videoId"],
            "live": video["liveNow"] or video["premium"],
            "upcoming": video["isUpcoming"],
        },
        youtube_video,
    )
)
print(youtube_video_df)

youtube_live = requests.get("https://invidious.snopyta.org/api/v1/search?q=" + quote_plus(" OR ".join(jp50)) + "&date=today&features=live", headers=headers).json()
youtube_live_df = pd.DataFrame(
    map(
        lambda live: {
            "url": "https://www.youtube.com/watch?v=" + live["videoId"],
            "live": live["liveNow"] or live["premium"],
            "upcoming": live["isUpcoming"],
        },
        youtube_live,
    )
)
print(youtube_live_df)

twitter = feedparser.parse(requests.get("https://nitter.pussthecat.org/search/rss?f=tweets&q=" + quote_plus("lang:ja min_faves:10000")).text).entries
twitter_df = pd.DataFrame(
    map(
        lambda status: {
            "url": status.link.replace("#m", "").replace("nitter.pussthecat.org", "twitter.com"),
        },
        twitter,
    )
)
print(twitter_df)

df = pd.concat([youtube_video_df, youtube_live_df, twitter_df], ignore_index=True)
final_df = df.drop_duplicates(subset=["url"], ignore_index=True)
print("Deduplication:", len(df), "->", len(final_df))

out = Path("public/api.json")
print(f"Saving into {out}")
out.parent.mkdir(parents=True, exist_ok=True)
final_df.to_json(out, orient="records")
