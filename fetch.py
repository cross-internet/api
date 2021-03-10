import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests

HIRA_KATA = [chr(i) for i in [*range(0x3040, 0x309F + 1), *range(0x30A0, 0x30FF + 1)]]
HEADERS = {"User-Agent": "Mozilla/5.0"}


def update_csv(path, df, after_concat):
    _path = Path(path)
    _df = pd.read_csv(_path) if _path.is_file() else pd.DataFrame()
    _df = pd.concat([df, _df])
    _df = after_concat(_df)
    _df.to_csv(path, index=False)


def fetch_invidious_domains():
    json = requests.get("https://api.invidious.io/instances.json").json()

    df = pd.DataFrame(
        map(
            lambda instance: {
                "name": instance[0],
                "type": instance[1]["type"],
                "software": instance[1]["stats"] and instance[1]["stats"].get("software"),
            },
            json,
        ),
        columns=["name", "type", "software"],
    )
    df = df[(df.type == "https") & (df.software.notnull())]
    return df


def fetch_invidious_videos(search_list, domain):
    json = requests.get("https://" + domain + "/api/v1/search?q=" + quote_plus(" | ".join(search_list)) + "&date=today&sort_by=view_count", headers=HEADERS).json()

    df = pd.DataFrame(
        map(
            lambda video: {
                "id": video["videoId"],
                "views": video["viewCount"],
                "published_at": datetime.fromtimestamp(video["published"]).astimezone(),
                "live_feature": video["isUpcoming"] or video["liveNow"] or video["premium"],
            },
            json,
        ),
        columns=["id", "views", "published_at", "live_feature"],
    )
    df = df[df.live_feature == False]
    return df


invidious_domains = fetch_invidious_domains()
print(invidious_domains)

invidious_videos = fetch_invidious_videos(random.choices(HIRA_KATA, k=int(len(HIRA_KATA) / 4)), "invidious.snopyta.org")
print(invidious_videos)

update_csv("public/invidious_videos.csv", invidious_videos, lambda df: df.drop_duplicates(subset=["id"]).sort_values(by=["views"], ascending=False))

for _, video in invidious_videos.iterrows():
    print(f"https://www.youtube.com/watch?v={video.id} ({video.views} views)")
