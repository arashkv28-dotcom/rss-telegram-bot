import feedparser
import requests
import os
import json

CHAT_ID = "@testandishepahlavi"
SEEN_FILE = "seen.json"
BOT_TOKEN = os.environ["BOT_TOKEN"]

CHANNELS = [
    {
        "name": "ایران اینترنشنال (یوتیوب)",
        "emoji": "🎬",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCat6bC0Wrqq9Bcq7EkH_yQw"
    },
    {
        "name": "رادیو فردا (یوتیوب)",
        "emoji": "🎬",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCqYCssczpdf9f9oNJPQKiIQ"
    },
    {
        "name": "رادیو فردا (اخبار)",
        "emoji": "📰",
        "url": "https://www.radiofarda.com/api/z-pqpiev-qpp"
    },
    {
        "name": "کوچه (یوتیوب)",
        "emoji": "🎬",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCeBoFG76S36uI1rSUj98YzA"
    },
    {
        "name": "من و تو (یوتیوب)",
        "emoji": "🎬",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCnUdm0u-2FRffBnxQYHuTHA"
    },
]


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def send_telegram(emoji, channel_name, title, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"{emoji} {channel_name}\n\n{title}\n\n🔗 {link}"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(f"Telegram response: {response.status_code}")


def main():
    seen = load_seen()

    for channel in CHANNELS:
        print(f"\nChecking: {channel['name']}")
        feed = feedparser.parse(channel["url"])

        print(f"Feed status: {feed.get('status', 'no status')}")
        print(f"Entries: {len(feed.entries)}")

        new_items = []
        for entry in feed.entries[:5]:
            title = entry.get("title", "بدون عنوان")
            link = entry.get("link", "")
            if link and link not in seen:
                new_items.append({"title": title, "link": link})

        print(f"New items: {len(new_items)}")

        for item in reversed(new_items):
            print(f"Sending: {item['title']}")
            send_telegram(channel["emoji"], channel["name"], item["title"], item["link"])
            seen.append(item["link"])

    save_seen(seen[-200:])
    print("\nDone!")


if __name__ == "__main__":
    main()
