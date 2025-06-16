
import os
import requests
import telegram
from bs4 import BeautifulSoup

REDIS_URL = os.getenv("REDIS_URL")
REDIS_TOKEN = os.getenv("REDIS_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=BOT_TOKEN)

headers = {
    "Authorization": f"Bearer {REDIS_TOKEN}",
    "Content-Type": "application/json"
}

def is_seen(ad_id):
    url = f"{REDIS_URL}/get/seen:{ad_id}"
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and response.json().get('result') is not None

def mark_seen(ad_id):
    url = f"{REDIS_URL}/set/seen:{ad_id}"
    payload = {"value": "1"}
    requests.post(url, headers=headers, json=payload)

def parse_ads(query):
    url = f"https://www.olx.ua/list/q-{query.replace(' ', '-')}/"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    ads = soup.select("a.css-z3gu2d")
    results = []

    for ad in ads:
        link = ad.get("href")
        if not link or not link.startswith("https://www.olx.ua/d/"):
            continue
        ad_id = link.split("-ID")[1].split(".html")[0]
        if is_seen(ad_id):
            continue
        mark_seen(ad_id)
        title = ad.select_one("h6").text if ad.select_one("h6") else "Без назви"
        results.append(f"🔹 <b>{title}</b>
{link}")
    return results

queries = [
    "фасувальне обладнання",
    "фасувальний станок",
    "пакувальне обладнання",
    "пакувальний станок"
]

for q in queries:
    ads = parse_ads(q)
    if not ads:
        print(f"❌ Немає нових по '{q}'")
        continue
    for ad in ads:
        bot.send_message(chat_id=CHAT_ID, text=ad, parse_mode=telegram.ParseMode.HTML)
