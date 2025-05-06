
import requests
import time
import html
import os
import telegram

OLX_TOKEN = os.environ.get("OLX_TOKEN")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "1900314873"))

HEADERS = {
    "Authorization": f"Bearer {OLX_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

SEARCH_QUERIES = [
    "фасувальне обладнання",
    "фасувальний станок",
    "пакувальне обладнання",
    "пакувальний станок"
]

seen_ids = set()
bot = telegram.Bot(token=BOT_TOKEN)

def get_ads_from_api(query):
    print(f"🔍 API запит: {query}")
    url = f"https://www.olx.ua/api/v1/offers/?limit=10&offset=0&query={query}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        offers = data.get("data", [])
        print(f"🔎 Отримано {len(offers)} оголошень")
        return offers
    print(f"❌ Помилка API: {res.status_code}")
    return []

def get_phone(ad_id):
    print(f"📞 Отримую номер для ID: {ad_id}")
    url = f"https://www.olx.ua/api/v1/offers/{ad_id}/limited-phones/"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0].get("number", "Не вказано")
    return "Не вдалося отримати"

def send_to_telegram(ad):
    ad_id = ad["id"]
    if ad_id in seen_ids:
        return
    seen_ids.add(ad_id)

    title = ad["title"]
    url = ad["url"]
    price = ad.get("price", {}).get("value", "Без ціни")
    location = ad.get("location", {}).get("label", "Без локації")
    phone = get_phone(ad_id)

    message = f"<b>{html.escape(title)}</b>\n" \
              f"{price} — {location}\n" \
              f"<a href='{url}'>Перейти до оголошення</a>\n" \
              f"📞 {phone}"
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)
    print(f"📩 Надіслано: {title}")

for query in SEARCH_QUERIES:
    ads = get_ads_from_api(query)
    for ad in ads:
        send_to_telegram(ad)
    time.sleep(2)
