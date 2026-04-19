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

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"links": [], "codes": []}

seen_links = set(data["links"])
seen_codes = set(data["codes"])

keywords = [
    "red packet", "ظرف", "binance",
    "thanks", "thank you", "شكرا",
    "fast", "ff", "fff", "ffff"
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
        json.dump({"links": list(seen_links), "codes": list(seen_codes)}, f)

@client.on(events.NewMessage)
async def handler(event):
    try:
        text = event.raw_text.lower()

        if not any(k in text for k in keywords):
            return

        links = re.findall(link_pattern, text)
        new_links = [l for l in links if l not in seen_links]

        codes = re.findall(code_pattern, text)

        clean_codes = []
        for c in codes:
            cleaned = remove_emoji(c)
            if cleaned not in seen_codes:
                seen_codes.add(cleaned)
                clean_codes.append(cleaned)

        if not new_links and not clean_codes:
            return

        msg = ""

        for l in new_links:
            seen_links.add(l)
            msg += f"🔗 {l}\n"

        for c in clean_codes:
            msg += f"🔑 {c}\n"

        if msg:
            send_to_bot(msg)
            save_data()

    except Exception as e:
        print("Error:", e)

client.start()
client.run_until_disconnected()
