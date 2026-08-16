import pandas as pd
import os

# Load Raw Dataset (handles .csv and .csv.gz)
raw_path = "data/raw/retail_sales_dataset.csv"
if not os.path.exists(raw_path) and os.path.exists(raw_path + ".gz"):
    raw_path += ".gz"

df = pd.read_csv(raw_path)

print("=" * 60)
print("RAW DATA SHAPE")
print(df.shape)


# Remove Duplicate Records
df = df.drop_duplicates()

# Handle Missing Values
df = df.fillna({
    "Discount": 0,
    "Returned": "No"
})

# Convert Date Column
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# Create Revenue Column
df["Revenue"] = df["Quantity"] * df["Unit_Price"] - df["Discount"]

# Save Clean Dataset
df.to_csv("data/processed/clean_sales_data.csv", index=False)

print("=" * 60)
print("CLEAN DATA SHAPE")
print(df.shape)

print("\nDataset Cleaned Successfully")