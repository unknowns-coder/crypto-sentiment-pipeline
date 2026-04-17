import os
import hashlib
import psycopg2
from dotenv import load_dotenv

from scraper import get_market_data
from analysis import create_sentiment_analyzer, get_sentiment_score


def load_environment():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
        return

    try:
        from dotenv import find_dotenv
        env_path = find_dotenv()
        if env_path:
            load_dotenv(env_path)
            print(f"✅ Loaded environment from {env_path}")
            return
    except ImportError:
        pass

    print("⚠️ .env file not found. Falling back to system environment variables.")


load_environment()

DATABASE_URL = os.getenv("DATABASE_URL")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "ProsusAI/finbert")
RSS_SOURCE = os.getenv("RSS_SOURCE", "Aggregated RSS")
DB_INIT_SQL = """
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    price NUMERIC(18, 8) NOT NULL,
    headline TEXT NOT NULL,
    sentiment VARCHAR(16) NOT NULL,
    confidence_score REAL NOT NULL,
    source TEXT NOT NULL,
    bundle_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def create_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in the environment")
    return psycopg2.connect(DATABASE_URL)


def initialize_db():
    connection = None
    try:
        connection = create_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(DB_INIT_SQL)
        connection.commit()
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize database schema: {exc}")
    finally:
        if connection is not None:
            connection.close()


def save_market_sentiment(price, headlines, sentiment, confidence_score, bundle_hash):
    query = """
    INSERT INTO market_data (price, headline, sentiment, confidence_score, source, bundle_hash)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (bundle_hash) DO NOTHING;
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
                    bundle_hash,
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

    try:
        initialize_db()
        save_market_sentiment(price, headlines_combined, sentiment, confidence_score, bundle_hash)
    except Exception as exc:
        print(f"❌ Pipeline Error: {exc}")


if __name__ == "__main__":
    run_pipeline()
