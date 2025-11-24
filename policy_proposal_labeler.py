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

    def is_user_spammer(self, actor: str, limit: int = 10) -> bool:
        """User suspicious if oldest of recent 10 posts < 24 hours"""
        params = {"actor": actor, "limit": limit}
        feed = self.client.app.bsky.feed.get_author_feed(params)

        post_dates = []
        for item in feed.feed:
            dt = datetime.fromisoformat(item.post.indexed_at.replace("Z", "+00:00"))
            post_dates.append(dt)

        if not post_dates:
            return False

        oldest = min(post_dates)
        now = datetime.now(timezone.utc)

        return (now - oldest < timedelta(days=1))

    def moderate_post(self, url: str) -> List[str]:
        labels = []

        # 1. Behavior signal
        actor = self.extract_actor(url)
        if actor and self.is_user_spammer(actor):
            labels.append(BEHAVIOR_LABEL)

        # 2. Text classification
        post_record = post_from_url(self.client, url)
        text = post_record.value.text

        cleaned = preprocess_text_single(text)
        X = self.vectorizer.transform([cleaned])
        pred = self.model.predict(X)[0]

        if pred == 1:
            risk = True

        # 3. Return int label
        return 0 if risk else 1
