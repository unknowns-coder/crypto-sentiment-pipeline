# Crypto Sentiment Pipeline

An End-to-End Data Engineering project that scrapes BTC/USD data, stores it in PostgreSQL, and uses AI for market sentiment analysis.

## Tech Stack
* **Language:** Python 3.11
* **Database:** PostgreSQL (Supabase)
* **Infrastructure:** Docker & GitHub Actions
* **AI:** Hugging Face (Sentiment Analysis)

## Status
- [x] Phase 1: Data Engineering (In Progress)
- [x] Phase 2: AI Integration
- [ ] Phase 3: DevOps & Deployment
- [ ] Phase 4: Automation & Delivery

## Usage
1. Create a `.env` file with `DATABASE_URL`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```bash
   python main.py
   ```

## Notes
- `main.py` now initializes the PostgreSQL table automatically before writing data.
- The pipeline stores a unique `bundle_hash` and avoids duplicate inserts.
- `analysis.py` now handles lowercase sentiment labels returned by `ProsusAI/finbert`.
- This README change was saved and committed locally for verification.
