# PhonePe Analytics Interview Prep Guide

## Your Project (say this in interview)

> "I built a **Digital Payment Transaction Analytics** system analyzing 50,000 UPI and digital payment transactions across 5,000 users for the year 2024. The project covers end-to-end analytics — data generation, EDA, business KPI dashboarding, and actionable insights — using Python, Pandas, Matplotlib/Seaborn, and an interactive Streamlit dashboard with Plotly."

---

## Tech Stack to Mention

| Tool | What you used it for |
|---|---|
| Python | Core analysis language |
| Pandas | Data loading, cleaning, groupby aggregations |
| NumPy | Statistical calculations, percentiles |
| Matplotlib + Seaborn | Static charts, heatmaps |
| Plotly | Interactive charts in dashboard |
| Streamlit | Web dashboard with filters |

---

## Key Metrics You Analyzed (memorize these)

- **GMV** (Gross Merchandise Value) — total payment value processed
- **Transaction Success Rate** — 94.6% in your dataset
- **Average Transaction Value (ATV)** — ₹2,129
- **DAU/MAU** — daily/monthly active users
- **Category-wise split** — Food, Travel, Shopping, etc.
- **Peak hour analysis** — 7 PM is peak (heatmap)
- **Cohort analysis** — spending by age group (18–24 vs 35–44 etc.)

---

## 10 Questions They Will Ask — With Answers

### Q1. Tell me about your analytics project.
> "I analyzed 50K digital payment transactions to extract business insights for a PhonePe-like platform. I looked at GMV trends, category spending patterns, city-wise performance, payment method success rates, and user demographics. The key finding was that **Travel** drives highest GMV despite being only 8% of volume — high-value but low-frequency. UPI is dominant at 55% of transactions. Peak time is 7–9 PM. I built a Streamlit dashboard with Plotly for interactive exploration."

---

### Q2. What is EDA? How did you do it here?
> "EDA — Exploratory Data Analysis — means understanding the data before modeling. I did:
> 1. Shape check — 50K rows, 16 columns
> 2. Null/missing value check — none in synthetic, but I'd use `df.isnull().sum()`
> 3. Distribution of amounts — right-skewed (log-normal)
> 4. Outlier detection — used percentile analysis (P95, P99)
> 5. Groupby aggregations — by city, category, payment method
> 6. Time series — monthly and quarterly trends"

---

### Q3. What is GMV and why is it important for PhonePe?
> "GMV is the total rupee value of all successful transactions processed through the platform. It's the #1 metric for a payments company — it determines revenue (take rate × GMV), shows growth, and helps compare with competitors. PhonePe monetizes through merchant fees, so higher GMV = higher revenue."

---

### Q4. What was your most interesting insight?
> "The most interesting finding was the **concentration of GMV**: the top 5% of transactions account for 31% of total GMV — a classic Pareto pattern. This means PhonePe should prioritize high-value user retention and offer premium experiences (travel, education bookings) to protect that segment. Also, Net Banking had the highest failure rate (~9%) — UX improvement opportunity there."

---

### Q5. How did you handle data cleaning?
> "The dataset was synthetically generated, so it was clean. But in real-world scenarios I would:
> - Remove duplicate transaction IDs
> - Handle NULL values (impute or drop depending on the column)
> - Fix data type mismatches (e.g., date columns stored as strings)
> - Cap outliers at P99 for amount fields
> - Validate referential integrity (e.g., all user_ids exist)
> Using `df.duplicated()`, `df.dtypes`, `df.describe()`, `df.isnull().sum()`"

---

### Q6. Explain groupby in Pandas. Give an example from your project.
> "`groupby` splits data by a column and applies aggregation. Example from my project:
> ```python
> city_gmv = df.groupby('city')['amount'].sum().sort_values(ascending=False)
> ```
> This gives total GMV per city. I used it for categories, payment methods, time periods, and demographics."

---

### Q7. What is a KPI? What KPIs did you track?
> "KPI = Key Performance Indicator — a measurable value that shows how effectively a business is achieving goals.
> My dashboard tracked:
> - **GMV** — business scale
> - **Transaction count** — volume
> - **Success rate** — platform reliability
> - **Average transaction value** — user spending behavior
> - **Active users** — engagement"

---

### Q8. What is the difference between mean and median? Which did you use for transaction amounts?
> "Mean is the average (sum/count) — sensitive to outliers. Median is the middle value — robust to outliers.
> For transaction amounts I used **both**: the mean was ₹2,129 but the median was lower because large travel transactions skew the mean upward. For reporting to business, I'd use median as 'typical transaction size' and mean for total GMV calculations."

---

### Q9. How would you detect fraud in this transaction data?
> "Good question — analytical approach:
> 1. **Velocity checks** — same user making 10+ transactions in 1 minute
> 2. **Amount anomaly** — Z-score or IQR method to flag unusual amounts
> 3. **Location mismatch** — transaction from Mumbai and Chennai within 10 minutes
> 4. **Time anomaly** — 3 AM transactions from users who never transact at night
> 5. **Merchant anomaly** — first-time merchant with high transaction value
> In Python: `df.groupby('user_id').resample('1T').count()` for velocity."

---

### Q10. How would you improve this project?
> "Three things:
> 1. **ML model** — predict transaction failure using features like amount, payment method, hour → LogisticRegression or XGBoost
> 2. **User segmentation** — K-means clustering on (frequency, monetary, recency) — RFM analysis
> 3. **Real-time dashboard** — connect to a live database instead of CSV, use WebSocket streaming in Streamlit"

---

## Resume Bullet Points (copy these)

```
• Built Digital Payment Transaction Analytics system analyzing 50K UPI transactions
  across 5K users using Python, Pandas, and Seaborn — identified ₹10Cr+ GMV patterns,
  peak-hour traffic, and payment method failure rates

• Developed interactive Streamlit dashboard with Plotly featuring live filters for city,
  category, payment method, and quarter — enabling drill-down business insights

• Applied EDA techniques including time-series trend analysis, demographic cohort analysis,
  and percentile-based distribution study to surface actionable insights (top 5% users = 31% GMV)
```

---

## How to Run This Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate dataset
python generate_data.py

# 3. Run EDA and save charts
python analysis.py

# 4. Launch interactive dashboard
streamlit run dashboard.py
```
