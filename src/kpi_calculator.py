import pandas as pd
import os

# Load Clean Dataset (handles .csv and .csv.gz)
clean_path = "data/processed/clean_sales_data.csv"
if not os.path.exists(clean_path) and os.path.exists(clean_path + ".gz"):
    clean_path += ".gz"

df = pd.read_csv(clean_path)


# Convert Date
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

print("=" * 60)
print("BUSINESS KPI REPORT")
print("=" * 60)

# ==========================
# Overall KPIs
# ==========================

total_revenue = df["Revenue"].sum()
total_orders = df["Order_ID"].nunique()
total_customers = df["Customer_ID"].nunique()
average_order_value = total_revenue / total_orders
total_quantity = df["Quantity"].sum()

print(f"Total Revenue        : ₹{total_revenue:,.2f}")
print(f"Total Orders         : {total_orders}")
print(f"Total Customers      : {total_customers}")
print(f"Average Order Value  : ₹{average_order_value:,.2f}")
print(f"Items Sold           : {total_quantity}")

# ==========================
# Category Performance
# ==========================

print("\nTop Categories by Revenue")

category_sales = (
    df.groupby("Category")["Revenue"]
      .sum()
      .sort_values(ascending=False)
)

print(category_sales)

# ==========================
# Region Performance
# ==========================

print("\nRegion Wise Revenue")

region_sales = (
    df.groupby("Region")["Revenue"]
      .sum()
      .sort_values(ascending=False)
)

print(region_sales)

# ==========================
# Monthly Revenue
# ==========================

df["Month"] = df["Order_Date"].dt.to_period("M")

monthly_sales = (
    df.groupby("Month")["Revenue"]
      .sum()
)

print("\nMonthly Revenue")

print(monthly_sales)

# ==========================
# Return Analysis
# ==========================

return_rate = (
    (df["Returned"] == "Yes").mean()
) * 100

print(f"\nReturn Rate : {return_rate:.2f}%")