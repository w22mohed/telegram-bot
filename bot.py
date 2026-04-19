import re
import os
import json
import requests
from telethon import TelegramClient, events

api_id = "39448341"
api_hash = "bc7184284bc452b668c8233864e79a2b"
bot_token = "8208733782:AAFs9pBhcCn9DRxRACoxqBexmzqE7QGMkGw"
chat_id = "6573315006"


client = TelegramClient("session", api_id, api_hash)

DATA_FILE = "data.json"

try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
except:
    data = {"items": []}

seen = set([item["value"] for item in data["items"]])

keywords = [
    "red packet", "ظرف", "binance",
    "thanks", "thank you", "شكرا",
    "fast", "ff", "fff", "ffff"
]

# قنوات ممنوعة
blacklist = [
    "ads", "spam"
]

link_pattern = r'https?://\S+'
code_pattern = r'(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&*()_+=!]{8,}(?:[\U00010000-\U0010ffff]*)'

def remove_emoji(text):
    return re.sub(r'[\U00010000-\U0010ffff]', '', text)

def send_to_bot(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"items": list(data["items"])}, f)

@client.on(events.NewMessage)
async def handler(event):

    # ❌ تجاهل الخاص
    if not event.is_group and not event.is_channel:
        return

    text = event.raw_text.lower()

    # 🚫 فلترة قنوات غير مهمة
    chat_title = (event.chat.title or "").lower() if event.chat else ""
    if any(b in chat_title for b in blacklist):
        return

    if not any(k in text for k in keywords):
        return

    source_name = event.chat.title if event.chat else "Unknown"
    source_id = event.chat_id
    source_link = f"https://t.me/c/{str(source_id)[4:]}" if str(source_id).startswith("-100") else "Private"

    links = re.findall(link_pattern, text)
    codes = re.findall(code_pattern, text)

    msg = f"📡 Source: {source_name}\n🔗 Link: {source_link}\n\n"

    for l in links:
        cleaned = l
        if cleaned not in seen:
            seen.add(cleaned)
            data["items"].append({
                "type": "link",
                "value": cleaned,
                "source": source_name
            })
            msg += f"🔗 {cleaned}\n"

    for c in codes:
        cleaned = remove_emoji(c)
        if cleaned not in seen:
            seen.add(cleaned)
            data["items"].append({
                "type": "code",
                "value": cleaned,
                "source": source_name
            })
            msg += f"🔑 {cleaned}\n"

    if "🔗" in msg or "🔑" in msg:
        send_to_bot(msg)
        save_data()

client.start()
print("Bot running...")
client.run_until_disconnected()
