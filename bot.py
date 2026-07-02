import feedparser
import requests
import os
import json

# ==========================================
# لیست منابع RSS
# ==========================================
RSS_SOURCES = [
    {
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCat6bC0Wrqq9Bcq7EkH_yQw",
        "name": "Iran International"
    },
    {
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCqYCssczpdf9f9oNJPQKiIQ",
        "name": "Radio Farda"
    },
]

CHAT_ID = "@testandishepahlavi"
SEEN_FILE = "seen.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]


# ==========================================
# مدیریت لیست "دیده‌شده‌ها" (جلوگیری از تکرار)
# ==========================================
def load_seen():
    """خواندن لیست لینک‌هایی که قبلاً فرستاده شده"""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # اطمینان از اینکه خروجی همیشه لیست باشد
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not read seen.json ({e}), starting fresh")
    return []


def save_seen(seen):
    """ذخیره لیست به‌روزشده"""
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


# ==========================================
# ارسال پیام به تلگرام
# ==========================================
def send_telegram(title, link, source_name):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    text = f"""🎬 {source_name}

{title}

🔗 {link}
"""

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    result = response.json()
    
    if result.get("ok"):
        print(f"✅ Sent successfully: {title[:50]}...")
        return True
    else:
        print(f"❌ Failed to send: {result}")
        return False


# ==========================================
# بررسی یک منبع RSS
# ==========================================
def process_source(source, seen_set):
    print(f"\n{'='*50}")
    print(f"Checking: {source['name']}")
    print(f"URL: {source['url']}")

    feed = feedparser.parse(source['url'])

    status = feed.get('status', 'unknown')
    print(f"Feed status: {status}")
    print(f"Number of entries: {len(feed.entries)}")

    if len(feed.entries) == 0:
        print("⚠️ No entries found!")
        if feed.get('bozo'):
            print(f"Bozo exception: {feed.bozo_exception}")
        return []

    new_items = []

    # فقط ۵ آیتم آخر رو چک می‌کنیم
    for entry in feed.entries[:5]:
        title = entry.get("title", "بدون عنوان").strip()
        link = entry.get("link", "").strip()

        if not link:
            continue

        # ⭐ نکته کلیدی: چک کردن دقیق در seen_set
        if link in seen_set:
            print(f"⏭️  Already sent: {title[:50]}...")
            continue

        print(f"🆕 New item found: {title[:50]}...")
        new_items.append({
            "title": title,
            "link": link,
            "source": source['name']
        })

    return new_items


# ==========================================
# تابع اصلی
# ==========================================
def main():
    # بارگذاری لیست دیده‌شده‌ها به‌صورت set (سریع‌تر برای جستجو)
    seen_list = load_seen()
    seen_set = set(seen_list)

    print(f"📋 Loaded {len(seen_set)} previously seen items")

    all_new_items = []

    # بررسی همه منابع
    for source in RSS_SOURCES:
        new_items = process_source(source, seen_set)
        all_new_items.extend(new_items)

    print(f"\n{'='*50}")
    print(f"📊 Total new items to send: {len(all_new_items)}")

    if not all_new_items:
        print("✅ Nothing new to send. All caught up!")
        return

    # ارسال پیام‌ها (از قدیمی‌ترین به جدیدترین)
    sent_count = 0
    for item in reversed(all_new_items):
        success = send_telegram(item["title"], item["link"], item["source"])
        
        # فقط اگه با موفقیت فرستاده شد، به لیست seen اضافه کن
        if success:
            seen_list.append(item["link"])
            sent_count += 1

    print(f"\n✅ Successfully sent {sent_count} new items")

    # نگه داشتن فقط ۳۰۰ آیتم آخر (برای جلوگیری از رشد بی‌نهایت فایل)
    save_seen(seen_list[-300:])
    print(f"💾 Saved {len(seen_list[-300:])} items to seen.json")


if __name__ == "__main__":
    main()
