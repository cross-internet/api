from datetime import datetime
from pathlib import Path
from pprint import pprint

import pandas as pd

import utils

# API
invidious = utils.InvidiousAPI("invidious.snopyta.org")
twitter = utils.TwitterAPI()

# Path
path = Path("public/article.csv")
json_path = Path("public/article.json")

# 後述する処理で空のデータが帰ってくる確率を下げる
pprint(invidious.stats())

# 動画を取得する
invidious_videos = invidious.today_videos()
youtube_videos_df = pd.DataFrame(
    map(
        lambda video: {
            "url": "https://www.youtube.com/watch?v=" + video["videoId"],
            "date": datetime.fromtimestamp(video["published"]).astimezone().isoformat(),
            "traffic": video["viewCount"],
        },
        filter(
            lambda video: not (video["liveNow"] or video["premium"] or video["isUpcoming"]),
            invidious_videos,
        ),
    )
)
print(youtube_videos_df)

# ツイートを取得する
tweets = twitter.today_tweets()
tweets_df = pd.DataFrame(
    map(
        lambda tweet: {
            "url": "https://twitter.com/" + tweet["user"]["screen_name"] + "/status/" + tweet["id_str"],
            "date": datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y").isoformat(),
            "traffic": tweet["favorite_count"],
        },
        tweets,
    )
)
print(tweets_df)

# 読み込み
df = pd.read_csv(path) if path.is_file() else pd.DataFrame()

# 追加
df = pd.concat([youtube_videos_df, tweets_df, df], ignore_index=True)

# 最適化
df = df.drop_duplicates(subset=["url"], ignore_index=True).sort_values(by=["traffic"], ascending=False, ignore_index=True)
df = df[pd.to_datetime(df.date) > utils.YESTERDAY].reset_index(drop=True)

# 書き込み
path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(path, index=False)
json_path.parent.mkdir(parents=True, exist_ok=True)
df.to_json(json_path, orient="records")
