import requests
import os
import json
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_KEY = os.environ["YOUTUBE_API_KEY"]

CHAT_ID = "@allephba"
SEEN_FILE = "seen_allephba.json"
PAGE_FILE = "page_token.json"

PLAYLIST_ID = "PLxBEFYIvfmx0evzqZ716zA7UTqcinx5j9"


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
    text = f"🎬 ویدیوی جدید\n\n{title}\n\n🔗 {link}"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(f"Sent: {title[:50]} - Status: {response.status_code}")
    time.sleep(3)


def get_videos(page_token=""):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={PLAYLIST_ID}&maxResults=50&key={API_KEY}"
    if page_token:
        url += f"&pageToken={page_token}"
    response = requests.get(url)
    return response.json()


def main():
    seen = load_json(SEEN_FILE, [])
    page_token = load_json(PAGE_FILE, {}).get("token", "")

    print(f"Playlist: {PLAYLIST_ID}")
    data = get_videos(page_token)

    print(f"Total items in page: {len(data.get('items', []))}")

    videos = []
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["snippet"]["resourceId"]["videoId"]
        link = f"https://www.youtube.com/watch?v={video_id}"

        if link not in seen:
            videos.append({"title": title, "link": link})

    print(f"Videos to send: {len(videos)}")

    for video in reversed(videos):
        send_telegram(video["title"], video["link"])
        seen.append(video["link"])

    save_json(SEEN_FILE, seen)

    next_token = data.get("nextPageToken", "")
    save_json(PAGE_FILE, {"token": next_token})

    if next_token:
        print("More videos available. Run again!")
    else:
        print("All videos processed!")


if __name__ == "__main__":
    main()
