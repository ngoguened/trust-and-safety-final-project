import os
import pandas as pd
from datetime import datetime, timezone, timedelta

from atproto import Client
from dotenv import load_dotenv

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")


#get uerId from postLink
def extract_actor(url: str) -> str:
    parts = url.split("/profile/")[1]
    actor = parts.split("/")[0]
    return actor


def check_user_scam(client, actor: str, limit=5) -> bool:
    params = {
        "actor": actor,
        "limit": limit
    }

    feed = client.app.bsky.feed.get_author_feed(params)

    post_dates = []

    for item in feed.feed:
        indexed_at_str = item.post.indexed_at
        dt = datetime.fromisoformat(indexed_at_str.replace("Z", "+00:00"))
        post_dates.append(dt)

    oldest = min(post_dates)
    now = datetime.now(timezone.utc)

    return (now - oldest < timedelta(days=1))


def main():
    client = Client()
    client.login(USERNAME, PW)

    df = pd.read_csv(
        r"test-data/scam.csv",
        header=None,
        names=["url"]
    )

    scam_count = 0

    for url in df["url"]:
        actor = extract_actor(url)
        is_scam = check_user_scam(client, actor)
        if is_scam:
            scam_count += 1

    print("\nTotal SCAM:", scam_count)


if __name__ == "__main__":
    main()
