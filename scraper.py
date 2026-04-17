import requests
from bs4 import BeautifulSoup

BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
GOOGLE_RSS_URL = (
    "https://news.google.com/rss/search?q=bitcoin+when:1h&hl=en-US&gl=US&ceid=US:en"
)
HEADLINE_FALLBACK = ["Bitcoin market remains steady"]


def get_market_data():
    try:
        price_res = requests.get(BINANCE_PRICE_URL, timeout=10)
        price_res.raise_for_status()
        price = float(price_res.json().get("price", 0.0))

        rss_res = requests.get(GOOGLE_RSS_URL, timeout=10)
        rss_res.raise_for_status()
        soup = BeautifulSoup(rss_res.content, features="xml")

        items = soup.find_all("item")[:5]
        headlines = []
        for item in items:
            title = item.title.text if item.title else ""
            if title:
                headlines.append(title.split(" - ")[0].strip())

        if not headlines:
            headlines = HEADLINE_FALLBACK

        return price, headlines
    except Exception as exc:
        print(f"❌ Scraper Error: {exc}")
        return 0.0, []
