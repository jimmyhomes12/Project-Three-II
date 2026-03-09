# Tableau Public – E‑com RFM Dashboard Setup

This guide maps **your repo’s CSV files** to the click-by-click tutorial and answers: **Relationship vs Blend**, **customers measure**, and **Category/Device filters**.

---

## 0) Repo files (what you have)

| File | Location | Header row |
|------|----------|------------|
| **RFM scores (per customer)** | `data/rfm_scores.csv` | `customer_id, r_score, f_score, m_score, recency_days, frequency, total_revenue` |
| **RFM segments (aggregated)** | `output/rfm_segments.csv` | `r_score, f_score, m_score, customers` |
| **Full e‑com transactions** | `data/full_ecom.csv` | `order_id, customer_id, category, sales_amount, order_date, device, promo_code, review_score` |
| **Synthetic sales (alt)** | `data/synthetic_ecommerce_sales_2025.csv` | `order_id, customer_id, product_category, sales_amount, purchase_date, device_type, promo_code, review_score` |

Your current workbook uses **rfm_segments.csv** + **synthetic_ecommerce_sales_2025.csv** and points to paths under `Project-Three-main`. To use this repo and get Category/Device + trend, switch to the setup below.

---

## 1) Which RFM file to use

- **Heatmap + KPIs only (no trend, no Category/Device):**  
  Use **`output/rfm_segments.csv`**.  
  - Heatmap: Rows = `r_score`, Columns = `f_score`, Color = **SUM(customers)**.  
  - No `customer_id` → you cannot join to transactions, so no trend and no Category/Device filter.

- **Full dashboard (heatmap + KPIs + trend + Category/Device):**  
  Use **`data/rfm_scores.csv`** as the main RFM source.  
  - Heatmap: Rows = `r_score`, Columns = `f_score`, Color = **COUNTD(customer_id)** (Count Distinct).  
  - Join to **`data/full_ecom.csv`** on `customer_id` (Relationship, see below).

**Recommendation:** Use **rfm_scores.csv + full_ecom.csv** so the heatmap, KPIs, and trend line can all respond to Category/Device.

---

## 2) Relationship vs Blend

- **Use a Relationship (recommended).**  
  - Data → New Data Source → Text file → **full_ecom.csv**.  
  - In the logical model, add both: **rfm_scores** (or the table from `rfm_scores.csv`) and **full_ecom**.  
  - Create a **Relationship** on **customer_id**.  
  - Set both `customer_id` fields to **String** (avoids type mismatch and leading-zero issues).

- **Use Blend only** if you can’t add a Relationship (e.g. Tableau Public limitations). Then: primary = RFM source, secondary = full_ecom; link by `customer_id` and ensure the link icon is active when `customer_id` is in the view. Blending can be finicky for filtering.

---

## 3) “Customers” measure

- **If using `rfm_scores.csv`:**  
  - Heatmap color: drag **customer_id** to Color → set the pill to **Count (Distinct)**.  
  - KPI “Customers”: same **COUNTD(customer_id)**.

- **If using `rfm_segments.csv`:**  
  - Heatmap color and customer KPI: **SUM(customers)**.

---

## 4) Revenue and trend (full_ecom)

- **Revenue:** Use **SUM(sales_amount)** from **full_ecom** (after relationship). Optionally you can use **SUM(total_revenue)** from **rfm_scores** for a KPI that doesn’t depend on the transaction table.
- **Trend line:**  
  - Columns: **order_date** (from full_ecom) → set to continuous (e.g. Month or Week).  
  - Rows: **SUM(sales_amount)**.  
  - Marks: Line.

---

## 5) Category / Device filters

- **Field names in `full_ecom.csv`:** **category**, **device** (not `product_category` / `device_type`).  
- Add **Category** and **Device** to Filters, then **Show Filter**.  
- In the dashboard: filter card menu (▼) → **Apply to Worksheets** → **Selected Worksheets** → check Heatmap, KPI Cards, and Sales Trend so all respond.

---

## 6) Tableau Public: Full build (heatmap + trend + filters)

Use **data/rfm_scores.csv** and **data/full_ecom.csv** from this repo. Paths below assume your project is at  
`.../Project-Three` (e.g. `C:/Users/.../New folder (2)/Project-Three`).

### Step 1 – New workbook and save as TWBX

1. Open **Tableau Public** → **New Workbook**.
2. **File → Save As** → name: `Ecom_RFM_Dashboard.twbx` → save in **`tableau_viz/`** (so data can be packaged).

### Step 2 – Connect RFM data first

1. Left pane **Connect**: **Text file** → browse to **`data/rfm_scores.csv`** → **Open**.
2. On the Data Source page, check the preview: columns `customer_id`, `r_score`, `f_score`, `m_score`, `total_revenue`.
3. If **customer_id** is not String: click the column’s type icon → **String**.
4. Click **Sheet 1** at the bottom.

### Step 3 – Add full_ecom and create Relationship

1. **Data → New Data Source** (or **Data → Connect to Data** and add another connection).
2. **Text file** → browse to **`data/full_ecom.csv`** → **Open**.
3. Go to the **Data Source** tab (or open the data model).
4. You should see two tables (e.g. **rfm_scores** and **full_ecom**). If Tableau shows a logical model / canvas:
   - Drag or add both tables if needed.
   - Create a **Relationship** between them: click **New Relationship** (or the relationship line) and match **customer_id** to **customer_id**.
5. Set **customer_id** to **String** in both tables if needed (column header → data type).
6. Return to a sheet when done.

### Step 4 – Build the RFM Heatmap sheet

1. Rename the sheet: right‑click **Sheet 1** → **Rename** → **RFM Heatmap**.
2. In the Data pane, from the **rfm_scores** (primary) source:
   - Drag **r_score** → **Rows**.
   - Drag **f_score** → **Columns**.
3. Make both **Discrete** (blue pills): if they’re green, right‑click each pill → **Convert to Discrete**.
4. Drag **customer_id** → **Marks → Color**. On the pill, set to **Measure → Count (Distinct)**.
5. **Marks** dropdown → **Square**. Adjust **Size** so squares fill the grid.
6. **Color** → **Edit Colors** → pick a sequential palette → **Use Full Color Range**.
7. Optional: drag **m_score** to **Filters** → **Show Filter** (slider for monetary tier).

### Step 5 – Build the Sales Trend sheet

1. **New Worksheet** (bottom tab) → rename to **Sales Trend**.
2. From **full_ecom** (or the combined model):
   - Drag **order_date** → **Columns**. Right‑click the pill → **Month** (or **Week**) and keep it **Continuous** (green).
   - Drag **sales_amount** → **Rows** → should become **SUM(sales_amount)**.
3. **Marks** → **Line**.
4. Optional: drag **category** or **device** to **Color** if the line chart stays readable.

### Step 6 – Build KPI Cards (optional)

1. **Duplicate** the RFM Heatmap sheet → rename to **KPI Cards**.
2. Remove **r_score** from Rows and **f_score** from Columns (drag pills off).
3. **Marks** → **Text**.
4. Drag **customer_id** to **Text** → set to **Count (Distinct)**. Drag **sales_amount** (or **total_revenue** from rfm_scores) to **Text** → **SUM**.
5. Format the text (e.g. “Customers: &lt;COUNTD(customer_id)&gt;” and “Revenue: &lt;SUM(...)&gt;”) Edit the text (double‑click the Text mark), add labels and the measures, and set font size to 18–24.

### Step 7 – Create the dashboard and add filters

1. **New Dashboard** (dashboard icon at bottom) → rename to **2025 E-com RFM Dashboard**.
2. **Dashboard → Size**: e.g. **Desktop Browser** or **Automatic**.
3. From **Sheets**, drag onto the dashboard:
   - **RFM Heatmap** (e.g. left or main area).
   - **Sales Trend** (e.g. below or right).
   - **KPI Cards** if you built them (e.g. top).
4. Add **Category** and **Device** filters:
   - On any sheet that uses **full_ecom** (e.g. Sales Trend), drag **category** to **Filters** → **OK** → right‑click the filter pill → **Show Filter**. Same for **device**.
   - Or add filters from the dashboard: **Dashboard** (left) → drag **Category** and **Device** from the data pane onto the dashboard (Tableau may prompt which sheet to add from).
5. For each filter card on the dashboard: click the **▼** on the card → **Apply to Worksheets** → **Selected Worksheets** → select **RFM Heatmap**, **KPI Cards**, **Sales Trend** (so all respond to Category/Device).

### Step 8 – Heatmap filter action (click cell → update trend + KPIs)

1. On the **dashboard**, menu **Dashboard → Actions**.
2. **Add Action → Filter**.
3. **Source Sheet**: **RFM Heatmap**. **Run action on**: **Select**.
4. **Target Sheets**: check **Sales Trend** and **KPI Cards** (and any other sheets that should respond).
5. **Clearing the selection will**: **Show all values**.
6. **OK**. Now clicking a heatmap cell filters the trend and KPIs.

### Step 9 – Publish and export for GitHub

1. **File → Save to Tableau Public** → name (e.g. “Project-Three RFM”). After publish, use **Share → Embed** for your README if needed.
2. **File → Export Packaged Workbook** (or **Save As** and choose .twbx) → save as **`tableau_viz/Ecom_RFM_Dashboard.twbx`** so the packaged workbook in the repo uses the correct data.

### Tableau Public notes

- **Relationships:** Tableau Public supports relationships in the same way as Desktop for text/CSV; use **Data → New Data Source** and the relationship on **customer_id**.
- If the relationship UI differs (e.g. “Edit Relationship” instead of a canvas), link **customer_id** to **customer_id** and set both to String.
- **Data limits:** Tableau Public has size limits; your CSVs (e.g. 800 rows for rfm_scores, 5k for full_ecom) are well within range.

---

## 7) Data path fix (existing .twb)

The existing **Ecom_RFM_Dashboard.twb** references:

- `.../Project-Three-main/output/rfm_segments.csv`
- `.../Project-Three-main/data/synthetic_ecommerce_sales_2025.csv`

This repo is **Project-Three** (no `-main`). So either:

1. **Reconnect in Tableau:**  
   Open the workbook → Data → [each connection] → replace file path with:  
   - `.../Project-Three/tableau_viz/../output/rfm_segments.csv`  
   - or `.../Project-Three/data/full_ecom.csv` (if you switch to full_ecom),  
   using the actual path to **this** repo on your machine, or  

2. **Start from the tutorial** with **Save As → Ecom_RFM_Dashboard.twbx** in **`tableau_viz/`**, connect to **data/rfm_scores.csv** and **data/full_ecom.csv** from this repo, then build the heatmap + KPIs + trend + filters as in the tutorial.

Saving as **.twbx** (File → Save As / Export Packaged Workbook) and saving into **`tableau_viz/`** keeps the CSVs with the workbook for GitHub.

---

## 7) Quick “no data” checklist

- **Scores discrete:** Right‑click **r_score** / **f_score** → **Convert to Discrete** (blue pills).  
- **Filters:** Temporarily set to “All” or remove to test.  
- **customer_id:** Both sides **String**; watch for leading zeros in CSV.  
- **Dashboard Actions:** Heatmap filter action → target sheets = KPI Cards + Sales Trend.  
- **Blend:** If using blend, ensure **customer_id** is in the view and the link icon is active.

---

## 9) Summary table (your files → tutorial)

| Tutorial idea | Your file | Your field / measure |
|---------------|-----------|------------------------|
| RFM heatmap (with trend + filters) | `data/rfm_scores.csv` | R/F: `r_score`, `f_score` (discrete). Color: **COUNTD(customer_id)**. Optional size/detail: `m_score`. |
| Customers count | `rfm_scores` | **COUNTD(customer_id)** |
| Revenue | `data/full_ecom.csv` (or rfm_scores) | **SUM(sales_amount)** or **SUM(total_revenue)** |
| Order Date | `full_ecom.csv` | **order_date** (continuous, e.g. Month) |
| Category / Device | `full_ecom.csv` | **category**, **device** |
| Join key | both | **customer_id** (String, Relationship) |

If you paste your exact RFM and full-dataset header rows in the future, the same mapping can be confirmed or adjusted (e.g. if you rename files or columns).
