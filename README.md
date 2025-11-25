


# Automated Bluesky Scam Redirect Detector
This project focuses on detecting scam posts on Bluesky that attempt to redirect users to external platforms.

## Workflow
Loads `data.csv`, which contains Bluesky post URLs and ground-truth labels (scam vs. non-scam) for test.  
Logs into Bluesky with the user information in `.env`.  
Uses `AutomatedLabeler` to predict whether a post is a scam redirect.  
Compares predictions with expected labels.  
Prints the number of correct predictions and the overall accuracy.  



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
## How to Run the Test

```shell
python test.py
```

Once running, the service will print its activity to the terminal.

To stop the service, press `Ctrl+C` in the terminal.
