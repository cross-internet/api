import random
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests

HIRA_KATA = [chr(i) for i in [*range(0x3040, 0x309F + 1), *range(0x30A0, 0x30FF + 1)]]
HEADERS = {"User-Agent": "Mozilla/5.0"}
YESTERDAY = datetime.now().astimezone() - timedelta(days=1)


def read_csv_and_concat(file, df):
    path = Path(file)
    file_df = pd.read_csv(path) if path.is_file() else pd.DataFrame()
    return pd.concat([df, file_df])


def fetch_invidious_domains():
    json = requests.get("https://api.invidious.io/instances.json").json()
    df = pd.DataFrame(
        map(
            lambda instance: [
                instance[0],
                instance[1]["type"],
                instance[1]["stats"] and instance[1]["stats"].get("error"),
            ],
            json,
        ),
        columns=["name", "type", "error"],
    )
    df = df[(df.type == "https") & (df.error.isnull())]
    return df


def fetch_invidious_videos(search_list, domain, **kwargs):
    json = requests.get("https://" + domain + "/api/v1/search?q=" + quote_plus(" | ".join(search_list)) + "&date=today&sort_by=view_count", **kwargs).json()
    df = pd.DataFrame(
        map(
            lambda video: [
                video["videoId"],
                video["viewCount"],
                datetime.fromtimestamp(video["published"]).astimezone().isoformat(),
                video["isUpcoming"] or video["liveNow"] or video["premium"],
            ],
            json,
        ),
        columns=["id", "views", "published_at", "live_feature"],
    )
    df = df[df.live_feature == False]
    return df


# invidious domains
invidious_domains = fetch_invidious_domains()
print(invidious_domains)

# invidious videos
invidious_videos = fetch_invidious_videos(random.choices(HIRA_KATA, k=int(len(HIRA_KATA) / 4)), "invidious.snopyta.org", headers=HEADERS)
print(invidious_videos)

# invidious videos (update)
df = read_csv_and_concat("public/invidious_videos.csv", invidious_videos)
df = df.drop_duplicates(subset=["id"])
df = df[pd.to_datetime(df.published_at) > YESTERDAY]
df = df.sort_values(by=["views"], ascending=False)
df = df.reset_index(drop=True)
df.to_csv("public/invidious_videos.csv", index=False)

# save as json
invidious_videos_df = pd.DataFrame(
    map(
        lambda row: [
            f"https://www.youtube.com/watch?v={row.id}",
            "https://" + random.choice(invidious_domains.name.values) + f"/watch?v={row.id}",
            row.published_at,
            row.views,
        ],
        [row for _, row in df.iterrows()],
    ),
    columns=["url", "alternative_url", "date", "traffic"],
)

invidious_videos_df.to_json("public/v2.json", orient="records")
