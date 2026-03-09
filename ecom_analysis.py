"""
ecom_analysis.py
----------------
1. Import CSV into SQLite (table: ecom)
2. Create SQL views: orders_view, customers_view
3. Run Promo ROI and RFM segmentation queries
4. Export results to CSV files in output/
5. Export Tableau-ready CSVs to data/ (rfm_scores.csv, full_ecom.csv)
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# ── Paths ──────────────────────────────────────────────────────────────────────
CSV_PATH = "data/synthetic_ecommerce_sales_2025.csv"
DB_PATH = "ecom.db"
OUTPUT_PROMO = "output/promo_roi.csv"
OUTPUT_RFM = "output/rfm_segments.csv"
OUTPUT_RFM_SCORES = "data/rfm_scores.csv"
OUTPUT_FULL_ECOM = "data/full_ecom.csv"

# ── 1. Load CSV → SQLite ───────────────────────────────────────────────────────
print("Loading CSV into SQLite …")
df = pd.read_csv(CSV_PATH)
sqlite_engine = create_engine(f"sqlite:///{DB_PATH}")

with sqlite_engine.begin() as conn:
    df.to_sql("ecom", conn, if_exists="replace", index=False)

print(f"  Loaded {len(df):,} rows into table 'ecom' in {DB_PATH}")

# ── 2. Create Views ────────────────────────────────────────────────────────────
ORDERS_VIEW = """
CREATE VIEW IF NOT EXISTS orders AS
SELECT
    order_id,
    customer_id,
    product_category,
    sales_amount,
    purchase_date,
    device_type,
    promo_code,
    review_score
FROM ecom;
"""

CUSTOMERS_VIEW = """
CREATE VIEW IF NOT EXISTS customers AS
SELECT
    customer_id,
    COUNT(DISTINCT order_id)  AS total_orders,
    SUM(sales_amount)         AS lifetime_value,
    AVG(sales_amount)         AS avg_order_value,
    AVG(review_score)         AS avg_review_score,
    MAX(purchase_date)        AS last_purchase_date
FROM ecom
GROUP BY customer_id;
"""

print("Creating views …")
with sqlite_engine.begin() as conn:
    conn.execute(text("DROP VIEW IF EXISTS orders"))
    conn.execute(text("DROP VIEW IF EXISTS customers"))
    conn.execute(text(ORDERS_VIEW))
    conn.execute(text(CUSTOMERS_VIEW))
print("  Views created: orders, customers")

# ── 3a. Promo ROI Query ────────────────────────────────────────────────────────
PROMO_ROI_SQL = """
SELECT promo_code,
       AVG(sales_amount) AS avg_order_value,
       COUNT(*)          AS orders,
       SUM(sales_amount) AS total_revenue
FROM ecom
WHERE promo_code != ''
GROUP BY promo_code
ORDER BY total_revenue DESC;
"""

print("\nRunning Promo ROI query …")
with sqlite_engine.connect() as conn:
    promo_df = pd.read_sql_query(PROMO_ROI_SQL, conn)

promo_df["avg_order_value"] = promo_df["avg_order_value"].round(2)
promo_df["total_revenue"] = promo_df["total_revenue"].round(2)
promo_df.to_csv(OUTPUT_PROMO, index=False)
print(f"  Saved → {OUTPUT_PROMO}")
print(promo_df.to_string(index=False))

# ── 3b. RFM Segmentation Query ─────────────────────────────────────────────────
RFM_SQL = """
WITH rfm AS (
  SELECT customer_id,
         JULIANDAY('2025-12-31') - JULIANDAY(MAX(purchase_date)) AS recency_days,
         COUNT(DISTINCT order_id)                                 AS frequency,
         SUM(sales_amount)                                        AS monetary
  FROM ecom
  GROUP BY customer_id
),
rfm_scored AS (
  SELECT
    NTILE(5) OVER (ORDER BY recency_days)   AS r_score,
    NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary DESC)  AS m_score
  FROM rfm
)
SELECT r_score, f_score, m_score, COUNT(*) AS customers
FROM rfm_scored
GROUP BY r_score, f_score, m_score
ORDER BY r_score, f_score, m_score;
"""

print("\nRunning RFM Segmentation query …")
with sqlite_engine.connect() as conn:
    rfm_df = pd.read_sql_query(RFM_SQL, conn)

rfm_df.to_csv(OUTPUT_RFM, index=False)
print(f"  Saved → {OUTPUT_RFM}")
print(rfm_df.to_string(index=False))

# ── 3c. Per-Customer RFM Scores (for Tableau relationship on customer_id) ──────
RFM_SCORES_SQL = """
WITH rfm AS (
  SELECT customer_id,
         JULIANDAY('2025-12-31') - JULIANDAY(MAX(purchase_date)) AS recency_days,
         COUNT(DISTINCT order_id)                                 AS frequency,
         SUM(sales_amount)                                        AS monetary
  FROM ecom
  GROUP BY customer_id
),
rfm_scored AS (
  SELECT customer_id,
         recency_days,
         frequency,
         monetary,
         NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
         NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
         NTILE(5) OVER (ORDER BY monetary DESC)  AS m_score
  FROM rfm
)
SELECT customer_id,
       r_score,
       f_score,
       m_score,
       recency_days,
       frequency,
       ROUND(monetary, 2) AS total_revenue
FROM rfm_scored
ORDER BY customer_id;
"""

print("\nExporting per-customer RFM scores …")
with sqlite_engine.connect() as conn:
    rfm_scores_df = pd.read_sql_query(RFM_SCORES_SQL, conn)

rfm_scores_df.to_csv(OUTPUT_RFM_SCORES, index=False)
print(f"  Saved → {OUTPUT_RFM_SCORES}  ({len(rfm_scores_df):,} customers)")

# ── 4. Export full_ecom.csv (Tableau-ready column names) ──────────────────────
print("\nExporting full_ecom.csv …")
full_ecom_df = df.rename(columns={
    "purchase_date":    "order_date",
    "product_category": "category",
    "device_type":      "device",
})
full_ecom_df.to_csv(OUTPUT_FULL_ECOM, index=False)
print(f"  Saved → {OUTPUT_FULL_ECOM}  ({len(full_ecom_df):,} rows)")

print("\nDone.")
