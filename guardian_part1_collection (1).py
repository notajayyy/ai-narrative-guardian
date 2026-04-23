# ============================================================
# "AI in the Headlines" — Guardian API Project
# PART 1: Data Collection + Sentiment Scoring
#
# What this file does:
#   Step 1 — Calls Guardian API and collects articles about AI
#   Step 2 — Adds sentiment scores to each article (TextBlob)
#   Step 3 — Uploads enriched data to Google BigQuery
#
# After this, all business questions are answered in SQL
# and visualised in Power BI
# ============================================================

import requests
import time
import pandas as pd
from textblob import TextBlob
from google.cloud import bigquery
import pandas_gbq

# ── STEP 1: CALL GUARDIAN API ────────────────────────────────
# Collecting articles about Artificial Intelligence
# The API returns results page by page (pagination)

base_url  = "https://content.guardianapis.com/search"
api_key   = "YOUR_API_KEY_HERE"
all_articles = []
page_size    = 50
current_page = 1
total_pages  = 1

print("Fetching articles from Guardian API...")

while current_page <= total_pages:
    params = {
        "q"           : "artificial intelligence",  # search topic
        "api-key"     : api_key,
        "page-size"   : page_size,
        "page"        : current_page,
        "show-fields" : "all",
        "show-tags"   : "all",
        "order-by"    : "newest"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data        = response.json()
        total_pages = data.get("response", {}).get("pages", 1)
        results     = data.get("response", {}).get("results", [])
        total_results = data.get("response", {}).get("total", 0)

        if not results:
            print("No more results.")
            break

        all_articles.extend(results)
        print(f"Page {current_page}/{total_pages} | Articles collected: {len(all_articles)}/{total_results}")
        current_page += 1
        time.sleep(1)  # pause 1 second between requests (API rate limit)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        break

print(f"\nTotal articles collected: {len(all_articles)}")

# ── STEP 2: CONVERT TO DATAFRAME + BASIC CLEAN ───────────────
df = pd.DataFrame(all_articles)

# Save raw data as backup
df.to_csv("guardian_ai_raw.csv", index=False)
print("Raw data saved to guardian_ai_raw.csv")

# ── STEP 3: ADD SENTIMENT SCORES ─────────────────────────────
# TextBlob reads each article headline and gives a polarity score:
#   +1 = very positive  |  0 = neutral  |  -1 = very negative
# We label each article as Positive, Neutral, or Negative
# This is the ONLY thing Python does that SQL cannot do

print("\nRunning sentiment analysis on headlines...")

df['sentiment_score'] = df['webTitle'].apply(
    lambda x: TextBlob(str(x)).sentiment.polarity
)

df['sentiment_label'] = df['sentiment_score'].apply(
    lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
)

print(f"Sentiment scoring complete.")
print(f"  Positive : {(df['sentiment_label'] == 'Positive').sum()}")
print(f"  Neutral  : {(df['sentiment_label'] == 'Neutral').sum()}")
print(f"  Negative : {(df['sentiment_label'] == 'Negative').sum()}")
print(f"  Avg score: {df['sentiment_score'].mean():.4f}")

# Save enriched data locally
df.to_csv("guardian_ai_with_sentiment.csv", index=False)
print("\nEnriched data saved to guardian_ai_with_sentiment.csv")

# ── STEP 4: UPLOAD TO GOOGLE BIGQUERY ────────────────────────
# This sends the enriched CSV (with sentiment) to BigQuery
# From BigQuery, SQL takes over to answer all business questions

print("\nUploading to BigQuery...")

client = bigquery.Client(project="youtube-data-api-461916")
destination_table = f"{client.project}.definitions.src_guardian_ai_enriched"

pandas_gbq.to_gbq(
    df,
    destination_table,
    project_id="youtube-data-api-461916",
    if_exists="replace"
)

print(f"Upload complete → {destination_table}")
print("\nNext step: Run guardian_sql_analysis.sql in BigQuery")
