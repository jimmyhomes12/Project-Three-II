# Project Three: 2025 E-com RFM Analysis (SQL + Tableau)

![SQL](https://img.shields.io/badge/SQL-SQLite-blue) ![Tableau](https://img.shields.io/badge/Tableau-Public-orange)

Analyzed 100k synthetic sales with SQLite CTEs → RFM segments → Interactive dashboard.

## Key Insights
- Identified 4,000+ VIP customers (5-5-5 segment) — see [`output/rfm_segments.csv`](output/rfm_segments.csv).
- Promo codes drove **20% avg order lift** — see [`output/promo_roi.csv`](output/promo_roi.csv).

## Tech Stack
- **SQL (DBeaver/SQLite):** RFM modeling with window functions and CTEs.
- **Tableau Public:** Heatmap + funnels — [view dashboard](https://public.tableau.com/app/profile/jimmyhomes12/viz/Project-Three-RFM/RFMHeatmap).

## RFM Revenue Heatmap (SQL + Tableau)

### Overview
This dashboard segments 2025 e‑commerce customers into RFM buckets (Recency, Frequency, Monetary) using SQL, then visualizes revenue concentration across segments in Tableau.

### Data modeling
- Built RFM table in SQLite with a CTE that computes `recency_days`, `frequency`, and `total_revenue` per `customer_id`, then assigns R/F/M scores using `NTILE(5)`.
- Joined the RFM table (`rfm_scores.csv`) to the full transactions table (`full_ecom.csv`) in Tableau on an explicit `customer_id` key to keep the model transparent.

### Visualization design
- Core view is a 5×5 RFM heatmap: **Rows = r_score**, **Columns = f_score**.
- Color encodes `SUM(total_revenue)` via a dedicated calculated field `[Calculation_RevenueColor]` to highlight where revenue is concentrated.
- `COUNTD(customer_id)` is retained for KPI cards and tooltips so each segment shows both "number of customers" and "segment revenue".

### Why SUM(total_revenue) for color
- Business users care first about "which segments drive the most revenue," not just "where are the most customers."
- Using revenue on color and customer count in secondary elements (KPIs/tooltips) balances business impact with customer context.
- This choice is documented in [TABLEAU_SETUP.md](tableau_viz/TABLEAU_SETUP.md) so others can reproduce or switch between revenue‑ and count‑based encoding.

---

## Tableau Dashboard

**Setup guide:** See [tableau_viz/TABLEAU_SETUP.md](tableau_viz/TABLEAU_SETUP.md) for CSV mapping, Relationship vs Blend, customers measure, and fixing data paths.

Interactive RFM heatmap published to Tableau Public — axes: **R-Score** (rows) × **F-Score** (columns), colour intensity = **SUM(total_revenue)** (`[Calculation_RevenueColor]`), with an **M-Score** parameter filter to drill into any monetary tier.

[![RFM Heatmap preview](https://public.tableau.com/static/images/Pr/Project-Three-RFM/RFMHeatmap/1_rss.png)](https://public.tableau.com/app/profile/jimmyhomes12/viz/Project-Three-RFM/RFMHeatmap)

> **Embed this viz in your own HTML page** — copy the iframe below:

```html
<iframe
  src="https://public.tableau.com/views/Project-Three-RFM/RFMHeatmap?:embed=y&:showVizHome=no&:display_count=yes"
  width="100%"
  height="600"
  frameborder="0"
  allowfullscreen>
</iframe>
```

## Overview
End-to-end pipeline: generate synthetic data → import CSV into SQLite → create SQL views → run analytical queries → export results to CSV.

## Files
| File | Purpose |
|------|---------|
| `generate_data.py` | Generates `data/synthetic_ecommerce_sales_2025.csv` (5 000 rows) |
| `ecom_analysis.py` | Loads CSV → SQLite, creates views, runs queries, exports CSVs |
| `data/synthetic_ecommerce_sales_2025.csv` | Synthetic dataset (raw) |
| `data/rfm_scores.csv` | Per-customer RFM scores (`customer_id, r_score, f_score, m_score, recency_days, frequency, total_revenue`) — used as the primary Tableau data source for the heatmap and relationships |
| `data/full_ecom.csv` | Full order data with Tableau-friendly column names (`order_id, customer_id, category, sales_amount, order_date, device, promo_code, review_score`) — used for the Sales Trend sheet |
| `output/promo_roi.csv` | Promo ROI query results |
| `output/rfm_segments.csv` | RFM segmentation query results (aggregated by score combination) |
| `tableau_viz/Ecom_RFM_Dashboard.twbx` | Packaged Tableau workbook (data bundled) |

## Dataset Columns
`order_id`, `customer_id`, `product_category`, `sales_amount`, `purchase_date`, `device_type`, `promo_code`, `review_score`

## Quick Start
```bash
# (optional) regenerate the dataset
python3 generate_data.py

# run the full pipeline
python3 ecom_analysis.py
```

Outputs:
- `output/rfm_segments.csv` — aggregated RFM heatmap data
- `output/promo_roi.csv` — promo code ROI summary
- `data/rfm_scores.csv` — per-customer RFM scores (Tableau primary source)
- `data/full_ecom.csv` — full order data (Tableau trend sheet)

Requires: `pandas`, `sqlalchemy` (`pip install pandas sqlalchemy`)

## SQL Views Created
**`orders`** — mirrors all columns in `ecom`  
**`customers`** — per-customer aggregates: `total_orders`, `lifetime_value`, `avg_order_value`, `avg_review_score`, `last_purchase_date`

## Queries
### Promo ROI
```sql
SELECT promo_code,
       AVG(sales_amount) AS avg_order_value,
       COUNT(*) AS orders,
       SUM(sales_amount) AS total_revenue
FROM ecom
WHERE promo_code != ''
GROUP BY promo_code
ORDER BY total_revenue DESC;
```

### RFM Segmentation
```sql
WITH rfm AS (
  SELECT customer_id,
         JULIANDAY('2025-12-31') - JULIANDAY(MAX(purchase_date)) AS recency_days,
         COUNT(DISTINCT order_id) AS frequency,
         SUM(sales_amount) AS monetary
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
```
