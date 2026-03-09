"""
Generate synthetic e-commerce sales data for 2025 and save to CSV.
"""

import random
import csv
from datetime import date, timedelta

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports", "Beauty", "Toys"]
DEVICES = ["mobile", "desktop", "tablet"]
PROMO_CODES = ["SAVE10", "SUMMER20", "WELCOME15", "FLASH30", "", "", "", ""]  # blanks = no promo
REVIEW_SCORES = [1, 2, 3, 4, 5]

random.seed(42)

start_date = date(2025, 1, 1)
end_date = date(2025, 12, 31)
num_days = (end_date - start_date).days

rows = []
order_id = 1
for _ in range(5000):
    customer_id = random.randint(1, 800)
    category = random.choice(CATEGORIES)
    sales_amount = round(random.uniform(10.0, 500.0), 2)
    purchase_date = start_date + timedelta(days=random.randint(0, num_days))
    device = random.choice(DEVICES)
    promo = random.choice(PROMO_CODES)
    review = random.choice(REVIEW_SCORES)
    rows.append([order_id, customer_id, category, sales_amount,
                 purchase_date.isoformat(), device, promo, review])
    order_id += 1

output_path = "data/synthetic_ecommerce_sales_2025.csv"
with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "product_category",
                     "sales_amount", "purchase_date", "device_type",
                     "promo_code", "review_score"])
    writer.writerows(rows)

print(f"Generated {len(rows)} rows → {output_path}")
