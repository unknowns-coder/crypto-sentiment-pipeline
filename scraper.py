import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_market_data():
    print("📡 Fetching live BTC price...")
    price_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
    price = float(price_res.json()['price'])

    print("📰 Scraping latest news headline...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    # Switching to a more stable news source for scraping
    news_res = requests.get("https://cryptopanic.com/news/bitcoin/", headers=headers)
    soup = BeautifulSoup(news_res.text, 'html.parser')
    
    # Looking for the news title class
    headline_tag = soup.find('span', class_='title-text')
    headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"
    
    return price, headline

def save_to_cloud(price, headline):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO market_data (price, headline, source) 
        VALUES (%s, %s, %s)
        ON CONFLICT (headline) DO NOTHING;
        """
        cur.execute(insert_query, (price, headline, 'CoinDesk'))
        
        conn.commit()
        print(f"✅ SUCCESS: Saved BTC @ ${price} | Headline: {headline[:50]}...")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    btc_price, latest_news = get_market_data()
    save_to_cloud(btc_price, latest_news)