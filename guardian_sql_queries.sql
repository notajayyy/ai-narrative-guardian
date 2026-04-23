-- ============================================================
-- "AI in the Headlines" — Guardian API Project
-- PART 2: Business Questions answered in SQL (BigQuery)
--
-- Run each query separately in BigQuery.
-- Export results as CSV and load into Power BI for dashboard.
--
-- First run the fact table setup below, then the 6 questions.
-- ============================================================


-- ── FACT TABLE SETUP ─────────────────────────────────────────
-- Builds a clean, structured table from the raw enriched data
-- Run this ONCE before the business questions below

CREATE OR REPLACE TABLE fact.guardian_ai_fact AS

WITH guardian_data AS (
  SELECT * FROM definitions.src_guardian_ai_enriched
),

all_tags AS (
  SELECT
    t.id,
    tagItems.type,
    tagItems.webTitle AS tagValue
  FROM guardian_data AS t,
  UNNEST(t.tags) AS tagItems
),

authors AS (
  SELECT
    id,
    STRING_AGG(tagValue, ', ')    AS authorName,
    COUNT(DISTINCT tagValue)       AS nAuthors
  FROM all_tags
  WHERE type = 'contributor'
  GROUP BY id
),

final AS (
  SELECT
    g.id,
    g.type,
    g.sectionId,
    g.sectionName,
    TIMESTAMP(g.webPublicationDate)         AS publishedDate,
    g.webTitle,
    g.webUrl,
    CAST(g.fields.wordcount   AS INT)       AS wordcount,
    CAST(g.fields.charCount   AS INT)       AS charCount,
    g.fields.productionOffice               AS productionOffice,
    g.fields.lang                           AS lang,
    TIMESTAMP(g.fields.lastModified)        AS lastModified,
    a.authorName,
    a.nAuthors,
    -- Sentiment columns added by Python (TextBlob)
    g.sentiment_score,
    g.sentiment_label,
    -- Pre/Post ChatGPT flag for A/B test (Q3)
    CASE
      WHEN TIMESTAMP(g.webPublicationDate) < '2022-11-01'
      THEN 'A — Pre-ChatGPT'
      ELSE 'B — Post-ChatGPT'
    END AS ab_group
  FROM guardian_data g
  LEFT JOIN authors a ON a.id = g.id
)

SELECT
  *,
  DATE_DIFF(lastModified, publishedDate, HOUR) AS editDiffHrs
FROM final;


-- ============================================================
-- BUSINESS QUESTIONS
-- ============================================================


-- ── Q1. IS AI NEWS COVERAGE GROWING OVER TIME? ───────────────
-- Load into Power BI as a line chart (x=month, y=articles)
SELECT
  FORMAT_TIMESTAMP('%Y-%m', publishedDate)  AS month,
  COUNT(*)                                   AS article_count
FROM fact.guardian_ai_fact
GROUP BY month
ORDER BY month;


-- ── Q2. IS THE OVERALL TONE POSITIVE, NEGATIVE OR NEUTRAL? ──
-- Load into Power BI as a donut or bar chart
SELECT
  sentiment_label,
  COUNT(*)                                        AS article_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM fact.guardian_ai_fact
GROUP BY sentiment_label
ORDER BY article_count DESC;


-- ── Q3. DID THE CHATGPT LAUNCH CHANGE AI SENTIMENT? (A/B) ───
-- Compares avg sentiment before and after ChatGPT (Nov 2022)
-- Use as a bar chart in Power BI — two bars, one per group
SELECT
  ab_group,
  COUNT(*)                              AS total_articles,
  ROUND(AVG(sentiment_score), 4)        AS avg_sentiment,
  ROUND(AVG(wordcount), 0)              AS avg_wordcount,
  COUNTIF(sentiment_label = 'Positive') AS positive_count,
  COUNTIF(sentiment_label = 'Negative') AS negative_count,
  COUNTIF(sentiment_label = 'Neutral')  AS neutral_count
FROM fact.guardian_ai_fact
GROUP BY ab_group
ORDER BY ab_group;


-- ── Q4. WHICH SECTIONS COVER AI THE MOST? ───────────────────
-- Load into Power BI as a horizontal bar chart
SELECT
  sectionName,
  COUNT(*)                              AS article_count,
  ROUND(AVG(wordcount), 0)              AS avg_wordcount,
  ROUND(AVG(sentiment_score), 4)        AS avg_sentiment
FROM fact.guardian_ai_fact
GROUP BY sectionName
ORDER BY article_count DESC
LIMIT 10;


-- ── Q5. WHICH PRODUCTION OFFICE IS MOST NEGATIVE? ───────────
-- Load into Power BI as a bar chart with conditional colours
SELECT
  productionOffice,
  COUNT(*)                              AS article_count,
  ROUND(AVG(sentiment_score), 4)        AS avg_sentiment,
  COUNTIF(sentiment_label = 'Negative') AS negative_articles,
  COUNTIF(sentiment_label = 'Positive') AS positive_articles
FROM fact.guardian_ai_fact
WHERE productionOffice IS NOT NULL
GROUP BY productionOffice
ORDER BY avg_sentiment ASC;


-- ── Q6. WHO ARE THE TOP AUTHORS COVERING AI? ────────────────
-- Load into Power BI as a table visual
SELECT
  authorName,
  COUNT(*)                              AS total_articles,
  ROUND(AVG(sentiment_score), 4)        AS avg_sentiment,
  ROUND(AVG(wordcount), 0)              AS avg_wordcount,
  MIN(DATE(publishedDate))              AS first_article,
  MAX(DATE(publishedDate))              AS latest_article
FROM fact.guardian_ai_fact
WHERE authorName IS NOT NULL
GROUP BY authorName
HAVING COUNT(*) >= 3
ORDER BY total_articles DESC
LIMIT 10;


-- ── BONUS: MONTHLY SENTIMENT TREND ──────────────────────────
-- Shows how sentiment has shifted month by month
-- Load into Power BI as a line chart
SELECT
  FORMAT_TIMESTAMP('%Y-%m', publishedDate)  AS month,
  COUNT(*)                                   AS article_count,
  ROUND(AVG(sentiment_score), 4)             AS avg_sentiment,
  COUNTIF(sentiment_label = 'Positive')      AS positive,
  COUNTIF(sentiment_label = 'Negative')      AS negative
FROM fact.guardian_ai_fact
GROUP BY month
ORDER BY month;


-- ── Q7. WHICH SECTION WRITES THE LONGEST ARTICLES? ──────────
-- Tells us which sections invest more depth in AI coverage
-- Load into Power BI as a horizontal bar chart
SELECT
  sectionName,
  COUNT(*)                        AS article_count,
  ROUND(AVG(wordcount), 0)        AS avg_wordcount,
  MAX(wordcount)                  AS longest_article,
  MIN(wordcount)                  AS shortest_article
FROM fact.guardian_ai_fact
WHERE wordcount IS NOT NULL
GROUP BY sectionName
HAVING COUNT(*) >= 5
ORDER BY avg_wordcount DESC
LIMIT 10;


-- ── Q8. WHICH DAY OF THE WEEK HAS THE MOST AI COVERAGE? ─────
-- Useful for understanding editorial publishing patterns
-- Load into Power BI as a bar chart ordered Mon-Sun
SELECT
  FORMAT_TIMESTAMP('%A', publishedDate)     AS day_of_week,
  COUNT(*)                                   AS article_count,
  ROUND(AVG(wordcount), 0)                   AS avg_wordcount,
  ROUND(AVG(sentiment_score), 4)             AS avg_sentiment
FROM fact.guardian_ai_fact
GROUP BY day_of_week
ORDER BY
  CASE FORMAT_TIMESTAMP('%A', publishedDate)
    WHEN 'Monday'    THEN 1
    WHEN 'Tuesday'   THEN 2
    WHEN 'Wednesday' THEN 3
    WHEN 'Thursday'  THEN 4
    WHEN 'Friday'    THEN 5
    WHEN 'Saturday'  THEN 6
    WHEN 'Sunday'    THEN 7
  END;


-- ── Q9. WHICH AUTHORS ARE MOST CONSISTENTLY NEGATIVE? ───────
-- Identifies authors with the most negative editorial tone
-- Load into Power BI as a table or bar chart
SELECT
  authorName,
  COUNT(*)                              AS total_articles,
  ROUND(AVG(sentiment_score), 4)        AS avg_sentiment,
  COUNTIF(sentiment_label = 'Negative') AS negative_count,
  ROUND(
    COUNTIF(sentiment_label = 'Negative') * 100.0 / COUNT(*), 1
  )                                     AS negative_pct
FROM fact.guardian_ai_fact
WHERE authorName IS NOT NULL
GROUP BY authorName
HAVING COUNT(*) >= 5
ORDER BY avg_sentiment ASC
LIMIT 10;


-- ── Q10. DID ARTICLE LENGTH CHANGE POST-CHATGPT? ────────────
-- Extends the A/B story: did ChatGPT make journalists write more?
-- Load into Power BI as a side-by-side bar chart
SELECT
  ab_group,
  COUNT(*)                        AS total_articles,
  ROUND(AVG(wordcount), 0)        AS avg_wordcount,
  ROUND(AVG(sentiment_score), 4)  AS avg_sentiment,
  ROUND(AVG(editDiffHrs), 1)      AS avg_edit_hrs
FROM fact.guardian_ai_fact
WHERE wordcount IS NOT NULL
GROUP BY ab_group
ORDER BY ab_group;
