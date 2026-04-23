# ============================================================
# "AI in the Headlines" — Guardian API Project
# PART 2: Sentiment Scoring + A/B Testing + Hypothesis Testing
#
# What this file does:
#   Step 1 — Loads the enriched CSV from Part 1
#   Step 2 — Scores sentiment using TextBlob
#   Step 3 — Runs A/B test: Pre vs Post ChatGPT launch
#   Step 4 — Runs hypothesis test to validate A/B result
#   Step 5 — Prints a clean findings summary
#
# All visualisations are handled in Power BI
# using the SQL query results from guardian_part2_sql.sql
# ============================================================

import pandas as pd
from textblob import TextBlob
from scipy import stats

# ── STEP 1: LOAD DATA ────────────────────────────────────────
df = pd.read_csv("guardian_ai_with_sentiment.csv")
df['publishedDate'] = pd.to_datetime(df['publsihedDate'])
df['year_month']    = df['publishedDate'].dt.to_period('M')

print(f"Loaded {len(df)} articles")
print(f"Date range: {df['publishedDate'].min().date()} → {df['publishedDate'].max().date()}")

# ── STEP 2: QUICK DATA CHECK ─────────────────────────────────
print("\nMissing values check:")
print(df[['sectionName', 'productionOffice', 'wordcount', 'authorName']].isnull().sum())
print(f"\nWordcount — avg: {df['wordcount'].mean():.0f} | min: {df['wordcount'].min()} | max: {df['wordcount'].max()}")

# ── STEP 3: SENTIMENT ANALYSIS ───────────────────────────────
# TextBlob scores each headline: -1 (very negative) to +1 (very positive)
# This is the only step Python does that SQL cannot do
# The sentiment columns are already added in Part 1 and uploaded to BigQuery
# Here we re-score locally to run the A/B test and hypothesis test

print("\nRunning sentiment analysis...")

df['sentiment'] = df['webTitle'].apply(
    lambda x: TextBlob(str(x)).sentiment.polarity
)
df['sentiment_label'] = df['sentiment'].apply(
    lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
)

print(f"\nSentiment breakdown:")
print(df['sentiment_label'].value_counts())
print(f"Average sentiment score: {df['sentiment'].mean():.4f}")
print("(-1 = very negative | 0 = neutral | +1 = very positive)")

# ── STEP 4: A/B TEST — PRE vs POST CHATGPT LAUNCH ───────────
# Group A = articles published before ChatGPT launch (pre Nov 2022)
# Group B = articles published after ChatGPT launch  (post Nov 2022)
# Question: Did ChatGPT's launch significantly change how AI is reported?

chatgpt_launch = pd.Timestamp('2022-11-01')

group_a = df[df['publishedDate'] <  chatgpt_launch]['sentiment']
group_b = df[df['publishedDate'] >= chatgpt_launch]['sentiment']

print(f"\nA/B Test — Pre vs Post ChatGPT Launch (Nov 2022)")
print(f"  Group A (Pre-ChatGPT)  : {len(group_a)} articles | avg sentiment: {group_a.mean():.4f}")
print(f"  Group B (Post-ChatGPT) : {len(group_b)} articles | avg sentiment: {group_b.mean():.4f}")
print(f"  Difference             : {(group_b.mean() - group_a.mean()):.4f}")

# ── STEP 5: HYPOTHESIS TEST (Welch's t-test) ─────────────────
# H0 (Null)      : There is NO significant difference in sentiment
#                  between pre and post ChatGPT articles
# H1 (Alternate) : Sentiment DID shift significantly post-ChatGPT
# Alpha          : 0.05 (industry standard significance threshold)
# Method         : Welch's t-test (used when group sizes may differ)

t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

print(f"\nHypothesis Test Results:")
print(f"  H0 : No significant sentiment shift pre vs post ChatGPT")
print(f"  H1 : Sentiment shifted significantly post-ChatGPT")
print(f"  T-statistic : {t_stat:.4f}")
print(f"  P-value     : {p_value:.4f}")
print(f"  Alpha       : 0.05")

if p_value < 0.05:
    print(f"\n  RESULT: REJECT H0 — Significant sentiment shift detected")
    print(f"  AI news sentiment changed meaningfully after ChatGPT launched")
else:
    print(f"\n  RESULT: FAIL TO REJECT H0 — No significant shift detected")
    print(f"  Any observed difference is likely due to random chance")

# ── STEP 6: ADDITIONAL SUMMARY STATS ────────────────────────
# These feed directly into Power BI dashboard context

print(f"\nSection breakdown (top 5):")
print(df['sectionName'].value_counts().head(5))

print(f"\nProduction office sentiment:")
print(df.groupby('productionOffice')['sentiment'].mean().sort_values().round(4))

print(f"\nTop authors by volume (min 3 articles):")
top_authors = (
    df[df['authorName'].notna()]
    .groupby('authorName')
    .agg(articles=('webTitle', 'count'), avg_sentiment=('sentiment', 'mean'))
    .query('articles >= 3')
    .sort_values('articles', ascending=False)
    .head(10)
)
print(top_authors)

# ── FINAL FINDINGS SUMMARY ───────────────────────────────────
print("\n" + "=" * 55)
print("PROJECT FINDINGS SUMMARY")
print("=" * 55)
print(f"Total articles analysed   : {len(df)}")
print(f"Date range                : {df['publishedDate'].min().date()} → {df['publishedDate'].max().date()}")
print(f"Overall sentiment         : {df['sentiment_label'].value_counts().index[0]} dominant")
print(f"Average sentiment score   : {df['sentiment'].mean():.4f}")
print(f"Pre-ChatGPT avg sentiment : {group_a.mean():.4f}")
print(f"Post-ChatGPT avg sentiment: {group_b.mean():.4f}")
print(f"Sentiment shift           : {'Statistically significant' if p_value < 0.05 else 'Not significant'} (p={p_value:.4f})")
print(f"Most covered section      : {df['sectionName'].value_counts().index[0]}")
print(f"Most negative office      : {df.groupby('productionOffice')['sentiment'].mean().idxmin()}")
print(f"Top author                : {top_authors.index[0]} ({top_authors['articles'].iloc[0]} articles)")
print()
print("Next step: Load guardian_part2_sql.sql results into Power BI")
