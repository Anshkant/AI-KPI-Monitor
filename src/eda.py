import pandas as pd
import os

# Load Dataset (handles .csv and .csv.gz)
path = "data/raw/retail_sales_dataset.csv"
if not os.path.exists(path) and os.path.exists(path + ".gz"):
    path += ".gz"

df = pd.read_csv(path)


print("=" * 60)
print("DATASET SHAPE")
print(df.shape)

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print(df.head())

print("\n" + "=" * 60)
print("COLUMN NAMES")
print(df.columns.tolist())

print("\n" + "=" * 60)
print("DATA TYPES")
df.info()

print("\n" + "=" * 60)
print("MISSING VALUES")
print(df.isnull().sum())

print("\n" + "=" * 60)
print("SUMMARY STATISTICS")
print(df.describe())

print("\nEDA COMPLETED SUCCESSFULLY ✅")