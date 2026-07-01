import feedparser
import requests
import os
import json

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCat6bC0Wrqq9Bcq7EkH_yQw"
CHAT_ID = "@testandishepahlavi"
SEEN_FILE = "seen.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def send_telegram(title, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🎬 ویدیوی جدید\n\n{title}\n\n🔗 {link}"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(f"Telegram response: {response.status_code} - {response.text}")


def main():
    print(f"Fetching RSS: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)

    print(f"Feed status: {feed.get('status', 'no status')}")
    print(f"Number of entries: {len(feed.entries)}")

    if len(feed.entries) == 0:
        print("No entries found!")
        print(f"Feed keys: {list(feed.keys())}")
        print(f"Feed bozo: {feed.bozo}")
        if feed.bozo:
            print(f"Bozo exception: {feed.bozo_exception}")
        return

    for i, entry in enumerate(feed.entries[:3]):
        print(f"Entry {i}: title={entry.get('title', 'N/A')}, link={entry.get('link', 'N/A')}")

    seen = load_seen()
    print(f"Already seen: {len(seen)} items")

    new_items = []
    for entry in feed.entries[:5]:
        title = entry.get("title", "بدون عنوان")
        link = entry.get("link", "")
        if link and link not in seen:
            new_items.append({"title": title, "link": link})

    print(f"New items to send: {len(new_items)}")

    for item in reversed(new_items):
        print(f"Sending: {item['title']}")
        send_telegram(item["title"], item["link"])
        seen.append(item["link"])

    save_seen(seen[-100:])
    print("Done!")


if __name__ == "__main__":
    main()
