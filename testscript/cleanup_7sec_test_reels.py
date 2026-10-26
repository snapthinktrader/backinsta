# testscript/cleanup_7sec_test_reels.py
# Clean up 7-second test reels on Facebook, YouTube, and check Instagram

import os
import pickle
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

FB_PAGE_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "1394981273691815")
IG_USER_ID = os.getenv("REACT_APP_INSTAGRAM_ACCOUNT_ID", "17841477569192718")
IG_TOKEN = os.getenv("REACT_APP_ACCESS_TOKEN")

# Known 7s test videos
FB_7SEC_IDS = [
    "2013842113398322",
    "1510619644136866",
    "1757861452167012",
    "1510537227762690",
    "1456862126397406"
]

YT_7SEC_IDS = [
    "kh17FRtLHUY",
    "B0Pbcd1ME78",
    "mc59d0bGIVA",
    "PVcYEZFPM-k"
]

def cleanup_facebook():
    print("\n--- [Facebook Page Cleanup] ---")
    if not FB_PAGE_TOKEN:
        print("FB_PAGE_ACCESS_TOKEN not found!")
        return

    for vid_id in FB_7SEC_IDS:
        url = f"https://graph.facebook.com/v21.0/{vid_id}?access_token={FB_PAGE_TOKEN}"
        resp = requests.delete(url)
        print(f"Deleting FB Video {vid_id}: status={resp.status_code}, response={resp.text}")

    # Verify remaining videos on page
    feed_url = f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}/videos?fields=id,title,description,length&access_token={FB_PAGE_TOKEN}"
    feed_resp = requests.get(feed_url).json()
    print("Remaining FB Videos:")
    for v in feed_resp.get("data", []):
        print(f" - ID: {v.get('id')}, Length: {v.get('length')}s, Title: {v.get('title') or v.get('description', '')[:30]}")

def cleanup_youtube():
    print("\n--- [YouTube Cleanup] ---")
    pickle_path = "youtube_token.pickle"
    if not os.path.exists(pickle_path):
        print("youtube_token.pickle not found!")
        return

    with open(pickle_path, "rb") as f:
        creds = pickle.load(f)

    yt = build("youtube", "v3", credentials=creds)

    for vid_id in YT_7SEC_IDS:
        try:
            yt.videos().delete(id=vid_id).execute()
            print(f"Deleted YouTube Video {vid_id} successfully.")
        except Exception as e:
            print(f"Deleting YouTube Video {vid_id} failed: {e}")

def check_instagram():
    print("\n--- [Instagram Verification] ---")
    if not IG_TOKEN:
        print("REACT_APP_ACCESS_TOKEN not found!")
        return

    # Check published media list
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media?fields=id,caption,media_type,permalink,timestamp&access_token={IG_TOKEN}"
    resp = requests.get(url).json()
    items = resp.get("data", [])
    print(f"Found {len(items)} published posts on IG @usdaily24:")
    for item in items[:10]:
        print(f" - ID: {item.get('id')} | Type: {item.get('media_type')} | Link: {item.get('permalink')} | Caption: {item.get('caption', '')[:40]}")

if __name__ == "__main__":
    cleanup_facebook()
    cleanup_youtube()
    check_instagram()
