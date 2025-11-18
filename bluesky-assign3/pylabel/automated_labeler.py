"""Implementation of automated moderator"""

import re
from typing import List
from atproto import Client
import os
import pickle
from preprocessing.preprocess_text import preprocess_text_single

T_AND_S_LABEL = "t-and-s"

def _extract_post_id(url: str) -> str:
    """Extracts the unique post identifier from a Bluesky URL."""
    # This is a placeholder regex—adjust based on your actual URLs.
    match = re.search(r'/post/([\w\d]+)$', url)
    if match:
        return match.group(1)
    raise ValueError(f"Could not parse post ID from URL: {url}")

class AutomatedLabeler:
    """Automated labeler implementation using a trained Logistic Regression model."""

    def __init__(self, client:Client, input_dir: str): 
        self.client = client
        self.model = None
        self.vectorizer = None
        
        model_path = os.path.join(input_dir, 'trained_logistic_regression_model.pkl')
        vectorizer_path = os.path.join(input_dir, 'trained_count_vectorizer.pkl')
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
        except FileNotFoundError:
            print(f"Error: Model or vectorizer files not found in {input_dir}. Cannot moderate.")
            
   
    def moderate_post(self, url: str) -> List[str]:
        """
        Apply moderation to the post specified by the given url using the LR model.
        """
        if not self.model or not self.vectorizer:
            return []

        post_id = _extract_post_id(url)
        post_record = self.client.get_post(post_id)
        post_content = post_record['record']['text']
        
        cleaned_text = preprocess_text_single(post_content)
        
        X_new = self.vectorizer.transform([cleaned_text])
        
        prediction = self.model.predict(X_new)[0]
        
        if prediction == 1:
            return [T_AND_S_LABEL]
        
        return []