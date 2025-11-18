


# Real-time Bluesky Feed Labeler
The main script, `test_labeler.py`, runs in a continuous loop to provide live moderation:
1.  **Fetches Feeds**: The script fetches the latest posts from your "Following" timeline.
2.  **Analyzes Content**: Each new post is processed by a trained model to determine if it should be labeled.
3.  **Applies Labels**: If a post is flagged, the service will attempt to apply a `t-and-s` label to it on Bluesky.

## Setup Instructions

### 1. Configure Your Credentials
The service needs your Bluesky login credentials to interact with the AT Protocol.

1.  Create a file named `.env` in the root of the project directory.
2.  Add your credentials to the file in the following format, replacing the placeholder text with your actual handle and app password:
    ```
    USERNAME = "your-handle.bsky.social"
    PW = "your-app-password"
    ```

### 2. Install Dependencies
Ensure you have the necessary Python libraries installed by running
```shell
pip install -r requirements.txt
```
## How to Run the Service

To start the live moderation service, run the following command from the root of the project directory:

```shell
python test_labeler.py models
```

Once running, the service will print its activity to the terminal.

To stop the service, press `Ctrl+C` in the terminal.
