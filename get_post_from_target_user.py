import os
import pandas as pd
from datetime import datetime, timezone, timedelta
from atproto import Client
from dotenv import load_dotenv

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")


# --------- helper functions ---------
def extract_actor(url: str) -> str:
    parts = url.split("/profile/")[1]
    actor = parts.split("/")[0]
    return actor


def check_user_spam(client, actor: str, limit=3) -> bool:
    """Return True if user posted >= limit posts within past 24 hours"""
    params = {"actor": actor, "limit": limit}
    feed = client.app.bsky.feed.get_author_feed(params)

    post_dates = []
    for item in feed.feed:
        dt = datetime.fromisoformat(item.post.indexed_at.replace("Z", "+00:00"))
        post_dates.append(dt)

    if not post_dates:
        return False

    newest = post_dates[0]     # most recent post
    oldest = post_dates[-1]    # 5th most recent post

    # Check if the spread between newest and oldest is within 24 hours
    return (newest - oldest) < timedelta(days=1)

# --------- main logic ---------
def main():
    client = Client()
    client.login(USERNAME, PW)

    df = pd.read_csv("data.csv")
    df = df[df["label"] == 1]

    spam_count = 0

    print("\n===== Checking ONLY label=1 posts =====\n")

    for i, row in df.iterrows():
        url = row["URL"]
        actor = extract_actor(url)

        is_spam = check_user_spam(client, actor)

        if is_spam:
            spam_count += 1
            print(f"[SPAMMER]   {actor}   URL: {url}")
        else:
            print(f"[NORMAL BEHAVIOR]   {actor}   URL: {url}")

    print("\n====================================")
    print(f"Total label=1 posts: {len(df)}")
    print(f"label=1 posts with high-frequency behavior (24h >=5): {spam_count}")
    print("====================================\n")


if __name__ == "__main__":
    main()
