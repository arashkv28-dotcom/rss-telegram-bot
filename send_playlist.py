import yt_dlp
import requests
import os
import json
import time

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLxBEFYIvfmx0evzqZ716zA7UTqcinx5j9"
CHAT_ID = "@allephba"
BOT_TOKEN = os.environ["BOT_TOKEN"]
SEEN_FILE = "seen_playlist_allephba.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
        except Exception as e:
            print(f"Warning: Could not read seen file ({e})")
    return set()


def save_seen(seen_set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_set), f, ensure_ascii=False, indent=2)


def get_playlist_videos(playlist_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        videos = info.get('entries', [])

    videos.reverse()
    return videos


def send_telegram(title, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"""🎬 {title}

{link}
"""
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })
    return response.json()


def main():
    print("Loading seen videos...")
    seen = load_seen()
    print(f"Previously sent: {len(seen)} videos")

    print(f"\nFetching playlist: {PLAYLIST_URL}")
    videos = get_playlist_videos(PLAYLIST_URL)
    total = len(videos)
    print(f"Total videos in playlist: {total}")

    sent_count = 0
    skipped_count = 0

    for i, video in enumerate(videos, 1):
        video_id = video.get('id', '')
        title = video.get('title', 'بدون عنوان')
        link = f"https://www.youtube.com/watch?v={video_id}"

        if video_id in seen:
            print(f"[{i}/{total}] ⏭️  Already sent: {title[:50]}...")
            skipped_count += 1
            continue

        print(f"[{i}/{total}] Sending: {title[:50]}...")

        result = send_telegram(title, link)

        if result.get('ok'):
            print(f"  ✅ Sent")
            seen.add(video_id)
            sent_count += 1
        else:
            print(f"  ❌ Failed: {result}")

        time.sleep(3)

    save_seen(seen)

    print(f"\n{'='*50}")
    print(f"✅ Done!")
    print(f"   Sent: {sent_count}")
    print(f"   Skipped (already sent): {skipped_count}")
    print(f"   Total in playlist: {total}")


if __name__ == "__main__":
    main()
