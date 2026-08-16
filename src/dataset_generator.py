import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime

fake = Faker()

np.random.seed(42)
random.seed(42)

regions = [
    "North", "South", "East", "West",
    "Central", "North-East", "North-West",
    "South-East", "South-West", "International"
]

categories = {
    "Electronics": [
        "Laptop",
        "Smartphone",
        "Headphones",
        "Monitor",
        "Keyboard"
    ],
    "Furniture": [
        "Chair",
        "Table",
        "Sofa",
        "Wardrobe",
        "Desk"
    ],
    "Office Supplies": [
        "Notebook",
        "Printer",
        "Pen",
        "Paper",
        "Marker"
    ],
    "Appliances": [
        "Mixer",
        "Microwave",
        "Refrigerator",
        "Fan",
        "Air Conditioner"
    ]
}

records = []

for i in range(50000):

    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])

    quantity = random.randint(1,10)

    unit_price = random.randint(200,50000)

    discount = random.choice([0,5,10,15,20])

    revenue = quantity * unit_price * (1-discount/100)

    cost = revenue * random.uniform(0.5,0.9)

    profit = revenue-cost

    records.append({

        "Order_ID":100000+i,

        "Order_Date":fake.date_between(
            start_date="-3y",
            end_date="today"
        ),

        "Customer_ID":"CUST"+str(random.randint(1000,9999)),

        "Customer_Name":fake.name(),

        "Region":random.choice(regions),

        "Category":category,

        "Product":product,

        "Quantity":quantity,

        "Unit_Price":unit_price,

        "Discount":discount,

        "Revenue":round(revenue,2),

        "Cost":round(cost,2),

        "Profit":round(profit,2),

        "Returned":random.choice(["Yes","No"]),

        "Sales_Channel":random.choice(
            ["Online","Offline"]
        )
    })

df = pd.DataFrame(records)

df.to_csv("data/retail_sales_dataset.csv",index=False)

print("Dataset Created Successfully")
print(df.head())
print(df.shape)