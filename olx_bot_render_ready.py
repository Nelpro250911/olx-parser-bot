
import requests
from bs4 import BeautifulSoup
import time
import html
import re
import os
import telegram

# ==== Налаштування через середовище ====
OLX_TOKEN = os.environ.get("OLX_TOKEN")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "1900314873"))

HEADERS = {
    "Authorization": f"Bearer {OLX_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

search_urls = [
    "https://www.olx.ua/list/q-фасувальне-обладнання/",
    "https://www.olx.ua/list/q-фасувальний-станок/",
    "https://www.olx.ua/list/q-пакувальне-обладнання/",
    "https://www.olx.ua/list/q-пакувальний-станок/"
]

seen_ads = set()
bot = telegram.Bot(token=BOT_TOKEN)

def extract_ad_id(url):
    match = re.search(r'/obyavlenie/.+-(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_phone(ad_id):
    api_url = f"https://www.olx.ua/api/v1/offers/{ad_id}/limited-phones/"
    res = requests.get(api_url, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0].get('number', 'Не вказано')
    return "Не вдалося отримати"

def get_ads(url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("div[data-cy='l-card']")

    ads = []
    for item in items:
        link_tag = item.select_one("a")
        title = item.select_one("h6")
        price = item.select_one("p[data-testid='ad-price']")
        location = item.select_one("p[data-testid='location-date']")

        if not link_tag or not title:
            continue

        ad_url = link_tag["href"]
        if ad_url in seen_ads:
            continue
        seen_ads.add(ad_url)

        ad_data = {
            "title": title.text.strip(),
            "url": ad_url,
            "price": price.text.strip() if price else "Без ціни",
            "location": location.text.strip() if location else "Без локації"
        }

        ads.append(ad_data)
    return ads

def send_to_telegram(ad):
    ad_id = extract_ad_id(ad['url'])
    phone = get_phone(ad_id) if ad_id else "ID не знайдено"

    message = f"<b>{html.escape(ad['title'])}</b>\n" \
              f"{ad['price']} — {ad['location']}\n" \
              f"<a href='{ad['url']}'>Перейти до оголошення</a>\n" \
              f"📞 {phone}"
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

for search_url in search_urls:
    ads = get_ads(search_url)
    for ad in ads:
        send_to_telegram(ad)
    time.sleep(2)
