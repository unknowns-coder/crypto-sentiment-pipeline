import os
import hashlib
import psycopg2
from dotenv import load_dotenv

from scraper import get_market_data
from analysis import create_sentiment_analyzer, get_sentiment_score

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SENTIMENT_MODEL = "ProsusAI/finbert"
RSS_SOURCE = "Aggregated RSS"


def create_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in the environment")
    return psycopg2.connect(DATABASE_URL)


def save_market_sentiment(price, headlines, sentiment, confidence_score, bundle_hash):
    query = """
    INSERT INTO market_data (price, headline, sentiment, confidence_score, source)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (headline) DO NOTHING;
    """
    connection = None

    try:
        connection = create_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    price,
                    headlines,
                    sentiment,
                    round(confidence_score, 4),
                    RSS_SOURCE,
                ),
            )
            connection.commit()

            if cursor.rowcount > 0:
                print(
                    f"✅ DATA SECURED: ${price:.2f} | Mood: {sentiment} ({confidence_score:.2%})"
                )
                print(f"   bundle_hash={bundle_hash}")
            else:
                print("⏭️ Duplicate data detected. Skipping database write.")

    except Exception as exc:
        print(f"❌ DB Error: {exc}")
    finally:
        if connection is not None:
            connection.close()


def run_pipeline():
    price, headlines = get_market_data()
    if price <= 0 or not headlines:
        print("⚠️ Missing data, skipping run.")
        return

    analyzer = create_sentiment_analyzer(SENTIMENT_MODEL)
    sentiment, confidence_score = get_sentiment_score(headlines, analyzer)

    headlines_combined = " | ".join(headlines)
    bundle_hash = hashlib.sha256(f"{price}|{headlines_combined}".encode()).hexdigest()

    print(f"🧐 Analyzing Top {len(headlines)} headlines...")
    print(f"   sentiment={sentiment}, confidence={confidence_score:.4f}")

    save_market_sentiment(price, headlines_combined, sentiment, confidence_score, bundle_hash)


if __name__ == "__main__":
    run_pipeline()
