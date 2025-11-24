"get users' id, and get recent 10 posts"

import os

from atproto import Client
from dotenv import load_dotenv

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")


def main():
    """Main function"""
    client = Client()
    client.login(USERNAME, PW)

    # Parameters must be passed as a dictionary for the new atproto SDK
    params = {
        "actor": "galanmccree.bsky.social",
        "limit": 10
    }

    try:
        feed = client.app.bsky.feed.get_author_feed(params)
    except Exception as e:
        print("Error fetching feed:", e)
        return

    if not feed.feed:
        print("This user has no public posts or does not exist.")
        return

    #Store
    post_texts = []

    for item in feed.feed:
        text = item.post.record.text
        post_texts.append(text)

    print("Collected post texts:")
    print(post_texts) 
    print("List size:", len(post_texts))


if __name__ == "__main__":
    main()
