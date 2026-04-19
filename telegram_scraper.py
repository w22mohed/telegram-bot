from telethon import TelegramClient, events
from telethon.tl.types import Chat, Channel
import requests
import re
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

client = TelegramClient("session", api_id, api_hash)

ADMIN_ID = int(CHAT_ID)
bot_running = True

link_pattern = r"https?://\S+"

links_set = set()
codes_set = set()
target_chats = []

def send_to_telegram(text):
    if bot_running:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def clean_link(link):
    if "app.binance.com/uni-qr/cpos/" in link:
        return link.split("?")[0]
    return link

def is_valid_code(code):
    return len(code) == 8 and not code.isalpha()

thanks_keywords = [
    "thanks", "thank you", "thx",
    "شكر", "شكرا", "شكراً"
]

async def main():
    dialogs = await client.get_dialogs()

    for d in dialogs:
        if isinstance(d.entity, (Chat, Channel)):
            target_chats.append(d.id)

    print("Bot is running live...")
    await client.run_until_disconnected()

@client.on(events.NewMessage)
async def handler(event):

    if event.chat_id not in target_chats:
        return

    text = event.raw_text
    if not text:
        return

    chat = await event.get_chat()
    chat_name = getattr(chat, "title", "Unknown")
    chat_link = f"https://t.me/{chat.username}" if hasattr(chat, "username") and chat.username else "Private Group"

    text_lower = text.lower()

    if any(k in text_lower for k in thanks_keywords):
        send_to_telegram(f"💬 THANKS MESSAGE:\n{text}\n\n📡 Source: {chat_name}\n{chat_link}")
        return

    if "go" in text_lower:
        links = re.findall(link_pattern, text)
        for link in links:
            clean = clean_link(link.strip())
            if clean not in links_set:
                links_set.add(clean)
                send_to_telegram(f"🚀 GO LINK:\n{clean}\n\n📡 Source: {chat_name}\n{chat_link}")

    if "app.binance.com" in text_lower:
        links = re.findall(link_pattern, text)
        for link in links:
            clean = clean_link(link.strip())
            if clean not in links_set:
                links_set.add(clean)
                send_to_telegram(f"🔗 BINANCE LINK:\n{clean}\n\n📡 Source: {chat_name}\n{chat_link}")

    codes = re.findall(r"(?<!\S)[A-Za-z0-9!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/\\|~]{8}(?!\S)", text)

    for code in codes:
        clean_code = code.strip().lower()

        if is_valid_code(clean_code):
            if clean_code not in codes_set:
                codes_set.add(clean_code)
                send_to_telegram(f"🔐 CODE:\n{code}\n\n📡 Source: {chat_name}\n{chat_link}")

client.start()
client.loop.run_until_complete(main())
