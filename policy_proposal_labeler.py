"""
Policy Proposal Labeler
Combining behavioral signals + LR text model.
"""

import os
import pickle
from typing import List
from datetime import datetime, timezone, timedelta

from atproto import Client
from preprocessing.preprocess_text import preprocess_text_single
from pylabel.label import post_from_url, label_post

T_AND_S_LABEL = "t-and-s"
BEHAVIOR_LABEL = "potential-suspicious-behavior"

class AutomatedLabeler:
    """Automated moderator combining:
    - User behavioral signals (posting frequency)
    - Logistic Regression text model
    """

    def __init__(self, client: Client, input_dir: str):
        self.client = client
        self.labeler_client = client.with_proxy("atproto_labeler", client.me.did)

        # Model + vectorizer paths
        model_path = os.path.join(input_dir, "trained_logistic_regression_model.pkl")
        vect_path = os.path.join(input_dir, "trained_count_vectorizer.pkl")

        # Load model and vectorizer
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(vect_path, "rb") as f:
                self.vectorizer = pickle.load(f)
        except Exception as e:
            print("ERROR: Failed to load model or vectorizer:", e)
            self.model = None
            self.vectorizer = None

    def extract_actor(self, url: str):
        url = url.strip()
        if "/profile/" not in url:
            return None
        try:
            return url.split("/profile/")[1].split("/")[0]
        except:
            return None

    def is_user_spammer(self, actor: str, limit: int) -> bool:
        """User suspicious if oldest of recent limit posts < 24 hours"""
        params = {"actor": actor, "limit": limit}
        feed = self.client.app.bsky.feed.get_author_feed(params)

        post_dates = []
        for item in feed.feed:
            dt = datetime.fromisoformat(item.post.indexed_at.replace("Z", "+00:00"))
            post_dates.append(dt)

        if not post_dates:
            return False

        newest = post_dates[0]     
        oldest = post_dates[-1]    
        return (newest - oldest) < timedelta(days=1)

    def moderate_post(self, url: str) -> int:
        """
            0 = safe
            1 = risk
        """
        #1. model predict
        try:
            post = post_from_url(self.client, url)
        except Exception as e:
            return 0
    
        text = post.value.text

        cleaned = preprocess_text_single(text)
        X = self.vectorizer.transform([cleaned])
        pred = self.model.predict(X)[0]     # 1=risky, 0=safe

        #if the post is risky
        if pred==1:

            #2. count recent number of posts
            #if user sent to many posts(>5) the last day, them mark as risky
            actor = self.extract_actor(url)
            is_spammer = False

            limit=3

            if actor:
                is_spammer = self.is_user_spammer(actor,limit)

            if is_spammer:
                return 1
        
        return 0 #safe

