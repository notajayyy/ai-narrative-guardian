# The AI Narrative — Sentiment & Trend Analysis (Guardian API)

## Project Overview
An end-to-end data analytics project analysing **31,356 articles** from The Guardian newspaper to understand how global media sentiment around **Artificial Intelligence** has evolved from 2000 to 2024 — and whether the **ChatGPT launch (Nov 2022)** significantly shifted how AI is reported.

---

## Key Findings
- **66.21%** of AI articles are Neutral, **21.64%** Positive, **12.15%** Negative
- Overall average sentiment score: **0.04** (slightly positive)
- AI news sentiment was **higher post-ChatGPT** (0.04) than pre-ChatGPT (0.03)
- Post-ChatGPT articles are **significantly longer** (~1,900 words vs ~1,100 words)
- **World News** is the most covered section with ~4,000 AI articles
- **Richard Norton-Taylor** is the top author with ~300 AI articles
- Sentiment dipped lowest around **2007–2009** (financial crisis era)
- AI coverage has grown **significantly year on year** since 2015

---

## Business Questions Answered

| # | Question | Tool |
|---|---|---|
| Q1 | Is AI news coverage growing over time? | SQL |
| Q2 | Is the overall tone positive, negative or neutral? | SQL + Sentiment |
| Q3 | Did the ChatGPT launch change AI sentiment? | SQL + A/B Test |
| Q4 | Which sections cover AI the most? | SQL |
| Q5 | Which sections are most positive/negative about AI? | SQL + Sentiment |
| Q6 | Who are the top authors covering AI? | SQL |
| Q7 | Which section writes the longest articles? | SQL |
| Q8 | Which day of the week has the most AI coverage? | SQL |
| Q9 | Which authors are most consistently negative? | SQL + Sentiment |
| Q10 | Did article length change post-ChatGPT? | SQL + A/B Test |

---

## Tools & Technologies
- **Python** — Pandas, Requests, TextBlob, SciPy
- **SQL** — Google BigQuery
- **Visualisation** — Power BI (2-page dashboard)

---

## Statistical Analysis
- **Sentiment Analysis** — TextBlob polarity scoring on 31,356 article headlines
- **A/B Testing** — Pre vs Post ChatGPT launch (Nov 2022) sentiment and article length comparison
- **Hypothesis Testing** — Welch's t-test to validate whether sentiment shift is statistically significant (p < 0.05)

---

## Project Flow

```
Step 1 — Python (guardian_part1_collection.py)
         → Call Guardian API and collect 31,356 articles
         → Score sentiment on each headline using TextBlob
         → Upload enriched data to Google BigQuery

Step 2 — Python (guardian_analysis_clean.py)
         → A/B Test: Pre vs Post ChatGPT launch
         → Hypothesis Test: Welch's t-test to validate sentiment shift

Step 3 — SQL (guardian_part2_sql.sql)
         → Build fact table in BigQuery
         → Answer all 10 business questions

Step 4 — Power BI
         → Page 1: Overview — coverage growth, sentiment breakdown, section analysis
         → Page 2: Deep Dive — ChatGPT shift, sentiment trend, top authors, article length
```

---

## Dashboard Preview
**Page 1 — Overview**
- AI Coverage Growth (2000–2024)
- Overall Sentiment Breakdown
- Top 10 Sections by AI Coverage
- AI Sentiment by Section — Positive vs Negative

**Page 2 — Deep Dive**
- Sentiment Shift: Pre vs Post ChatGPT
- Yearly AI Sentiment Trend (2000–2024)
- Top 10 Authors Covering AI
- Avg Article Length: Pre vs Post ChatGPT

---

## Files in this Repository

| File | Description |
|---|---|
| `guardian_part1_collection.py` | API data collection + sentiment scoring + BigQuery upload |
| `guardian_analysis_clean.py` | A/B testing + hypothesis testing + findings summary |
| `guardian_part2_sql.sql` | Fact table setup + 10 business questions in SQL |

---

## How to Run

1. Get a free Guardian API key at [open-platform.theguardian.com](https://open-platform.theguardian.com)
2. Replace `YOUR_API_KEY_HERE` in `guardian_part1_collection.py`
3. Set up a Google BigQuery project and replace `YOUR_PROJECT_ID`
4. Run `guardian_part1_collection.py` to collect and upload data
5. Run the fact table query in `guardian_part2_sql.sql` in BigQuery
6. Run each business question query and export as CSV
7. Run `guardian_analysis_clean.py` for A/B test and hypothesis test results
8. Load CSV exports into Power BI to build the dashboard

---


## 📸 Dashboard Preview

<img width="1257" height="765" alt="image" src="https://github.com/user-attachments/assets/50878832-2a3b-419b-b5c4-ad666390ab0f" />

<img width="1257" height="766" alt="image" src="https://github.com/user-attachments/assets/4e114924-6f2a-40b4-b856-9d5ce9084b1c" />


## 📄 Dashboard Report

[Download Power BI Dashboard (PDF)](./powerbi-dashboard.pdf)



## Author

**Ajay Lakra**
[linkedin.com/in/ajay-lakraa](https://linkedin.com/in/ajay-lakraa)
