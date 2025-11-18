"""Script for testing the automated labeler"""

import argparse
import json
import os
import time

import pandas as pd
from atproto import Client
from dotenv import load_dotenv

from pylabel import AutomatedLabeler, label_post, did_from_handle

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")

def main():
    """
    Main function for the test script
    """
    client = Client()
    client.login(USERNAME, PW)

    parser = argparse.ArgumentParser()
    parser.add_argument("models_dir", type=str)
    parser.add_argument("--input_urls", type=str, default=None)
    parser.add_argument("--emit_labels", action="store_true", default=True)
    args = parser.parse_args()

    labeler = AutomatedLabeler(client, args.models_dir)

    if args.input_urls:
        urls = pd.read_csv(args.input_urls)
        num_correct, total = 0, urls.shape[0]
        for _index, row in urls.iterrows():
            url, expected_labels = row["URL"], json.loads(row["Labels"])
            labels = labeler.moderate_post(url)
            if sorted(labels) == sorted(expected_labels):
                num_correct += 1
            else:
                print(f"For {url}, labeler produced {labels}, expected {expected_labels}")
            if args.emit_labels and (len(labels) > 0):
                label_post(client, labeler_client, url, labels)
        print(f"The labeler produced {num_correct} correct labels assignments out of {total}")
        print(f"Overall ratio of correct label assignments {num_correct/total}")
    else:
        processed_posts = set()
        print("Starting live labeling of your feed... Press Ctrl+C to stop.")
        while True:
            try:
                print("Checking for new posts...")
                feed = client.get_timeline()
                
                new_posts = []
                if feed and feed.feed:
                    for post in feed.feed:
                        if post.post.uri not in processed_posts:
                            new_posts.append(post)

                if not new_posts:
                    print("No new posts found.")
                else:
                    for post in reversed(new_posts):
                        post_url = f"https://bsky.app/profile/{post.post.author.handle}/post/{post.post.uri.split('/')[-1]}"
                        print(f"Processing post: {post_url}")
                        
                        labels = labeler.moderate_post(post_url)
                        if labels:
                            print(f"Labeling post {post_url} with {labels}")
                            if args.emit_labels:
                                # Use the main client for labeling instead of a proxy
                                label_post(client, client, post_url, labels)
                        
                        processed_posts.add(post.post.uri)

                sleep_interval = 5
                print(f"Waiting for {sleep_interval} seconds...")
                time.sleep(sleep_interval)

            except KeyboardInterrupt:
                print("\nStopping live labeling.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)


if __name__ == "__main__":
    main()
