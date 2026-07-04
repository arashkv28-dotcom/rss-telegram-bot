import requests
import os
import json
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_KEY = os.environ["YOUTUBE_API_KEY"]

CHAT_ID = "@postytan"
CHANNEL_ID = "UC42KXh3nHwOOkyyTM1XlBMQ"
SEEN_FILE = "seen_allephba.json"
PAGE_FILE = "page_token.json"

# پلی‌لیست‌هایی که نباید ارسال شوند
BLOCKED_PLAYLISTS = [
    "PLPWAzSSYdgUfONkCNxvK7pDsNQ5vX3RMT",
    "PLPWAzSSYdgUfUbnOHyaPOJmden-f56hig",
    "PLPWAzSSYdgUeqJVGOYjx_F_pqPeHxr5En",
    "PLPWAzSSYdgUfCltS9Nc5h8r9KJx9aOteU",
]

# کلمات کلیدی که نباید ارسال شوند
BLOCKED_KEYWORDS = [
    "اخبار جهان",
    "مذاکرات ایران و آمریکا",
    "انتخابات",
    "سیاست آمریکا",
]


def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_telegram(title, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🎬 به زبان ساده\n\n{title}\n\n🔗 {link}"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(f"Sent: {title[:50]} - Status: {response.status_code}")
    time.sleep(3)


def is_blocked(title):
    for keyword in BLOCKED_KEYWORDS:
        if keyword in title:
            return True
    return False


def get_blocked_video_ids():
    blocked_ids = []
    for playlist_id in BLOCKED_PLAYLISTS:
        page_token = ""
        while True:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={API_KEY}"
            if page_token:
                url += f"&pageToken={page_token}"
            response = requests.get(url)
            data = response.json()

            for item in data.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                blocked_ids.append(video_id)

            page_token = data.get("nextPageToken", "")
            if not page_token:
                break

    print(f"Total blocked videos: {len(blocked_ids)}")
    return blocked_ids


def get_upload_playlist_id():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={CHANNEL_ID}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_videos(playlist_id, page_token=""):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={API_KEY}"
    if page_token:
        url += f"&pageToken={page_token}"
    response = requests.get(url)
    return response.json()


def main():
    seen = load_json(SEEN_FILE, [])
    page_token = load_json(PAGE_FILE, {}).get("token", "")

    print("Getting blocked videos...")
    blocked_ids = get_blocked_video_ids()

    playlist_id = get_upload_playlist_id()
    print(f"Upload playlist: {playlist_id}")

    data = get_videos(playlist_id, page_token)

    videos = []
    skipped = 0

    for item in data.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["snippet"]["resourceId"]["videoId"]
        link = f"https://www.youtube.com/watch?v={video_id}"

        if link in seen:
            continue

        if video_id in blocked_ids:
            print(f"BLOCKED (playlist): {title[:50]}")
            seen.append(link)
            skipped += 1
            continue

        if is_blocked(title):
            print(f"BLOCKED (keyword): {title[:50]}")
            seen.append(link)
            skipped += 1
            continue

        videos.append({"title": title, "link": link})

    print(f"Videos to send: {len(videos)}")
    print(f"Skipped: {skipped}")

    for video in reversed(videos):
        send_telegram(video["title"], video["link"])
        seen.append(video["link"])

    save_json(SEEN_FILE, seen)

    next_token = data.get("nextPageToken", "")
    save_json(PAGE_FILE, {"token": next_token})

    if next_token:
        print(f"More videos available. Run again!")
    else:
        print("All videos processed!")


if __name__ == "__main__":
    main()
