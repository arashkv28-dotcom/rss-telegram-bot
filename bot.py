import feedparser
import requests
import os
import json

RSS_URL = "https://rss.app/feeds/GtMuIsNLc4lY0KnN.xml"
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

    text = f"""🎬 ویدیوی جدید

{title}

🔗 {link}
"""

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    print(response.text)


def main():
    feed = feedparser.parse(RSS_URL)

    seen = load_seen()

    new_items = []

    for entry in feed.entries[:5]:
        title = entry.get("title", "بدون عنوان")
        link = entry.get("link", "")

        if link and link not in seen:
            new_items.append({
                "title": title,
                "link": link
            })

    # از قدیمی به جدید ارسال کند
    for item in reversed(new_items):
        send_telegram(item["title"], item["link"])
        seen.append(item["link"])

    # فقط 100 لینک آخر را نگه دارد
    save_seen(seen[-100:])


if __name__ == "__main__":
    main()
