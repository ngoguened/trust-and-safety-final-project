import pandas as pd
from atproto import Client
from dotenv import load_dotenv
import os

from policy_proposal_labeler import AutomatedLabeler

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")


def main():
    client = Client()
    client.login(USERNAME, PW)

    labeler = AutomatedLabeler(client, "models")

    df = pd.read_csv("data.csv")

    total = len(df)
    num_correct = 0

    for _, row in df.iterrows():
        url = row["URL"]
        expected = int(row["label"])
        predicted = labeler.moderate_post(url)  # 0 or 1

        if expected == predicted:
            num_correct += 1

    print(f"Correct: {num_correct}/{total}")
    print(f"Accuracy: {num_correct/total:.4f}")


if __name__ == "__main__":
    main()
