
import pandas as pd

# 1. Load the dataset
df = pd.read_csv(
    "data/Amazon Sale Report.csv",
    low_memory=False
)

# 2. Remove unnecessary columns
df = df.drop(
    columns=["index", "Unnamed: 22"],
    errors="ignore"
)

# 3. Clean column names
df.columns = df.columns.str.strip()

# 4. Convert Date to datetime
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m-%d-%y",
    errors="coerce" #It converts a invalid date into NAT like 35-02-22-->NAT 
                      #because we don't have 35 day's in a month
)

# 5. Standardize category names
df["Category"] = df["Category"].str.strip().str.title()

# 6. Remove exact duplicate rows
df = df.drop_duplicates()

# 7. Create a copy for analysis
# Do not delete zero-quantity rows from the original data.
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")

print("=" * 45)
print("ECOMMERCE SALES ANALYSIS")
print("=" * 45)

# 8. Overall metrics
print("\n1. OVERALL METRICS")

print("Total records:", len(df))
print("Unique orders:", df["Order ID"].nunique())
print("Recorded amount (all statuses):",
      round(df["Amount"].sum(), 2))
print("Records with missing amount:", df["Amount"].isna().sum())
print("Total quantity recorded:", df["Qty"].sum())
print("Positive-quantity records:", (df["Qty"] > 0).sum())

# 9. Order status analysis
print("\n2. ORDER STATUS ANALYSIS")

status_analysis = df.groupby("Status").agg(
    Records=("Order ID", "size"),
    Unique_Orders=("Order ID", "nunique"),
    Recorded_Amount=("Amount", "sum"),
    Quantity=("Qty", "sum")
).sort_values("Records", ascending=False)

print(status_analysis)

# 10. Monthly recorded amount
print("\n3. MONTHLY RECORDED AMOUNT")

df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly_sales = df.groupby("Month").agg(
    Recorded_Amount=("Amount", "sum"),
    Quantity=("Qty", "sum"),
    Unique_Orders=("Order ID", "nunique")
)

print(monthly_sales)

# 11. Best-selling categories
print("\n4. TOP PRODUCT CATEGORIES")

category_sales = df[df["Qty"] > 0].groupby("Category").agg(
    Units_Sold=("Qty", "sum"),
    Recorded_Amount=("Amount", "sum"),
    Unique_Orders=("Order ID", "nunique")
).sort_values("Units_Sold", ascending=False)

print(category_sales.head(10))

# 12. Best-selling products by SKU
print("\n5. TOP 10 PRODUCTS BY QUANTITY")

product_sales = df[df["Qty"] > 0].groupby("SKU").agg(
    Units_Sold=("Qty", "sum"),
    Recorded_Amount=("Amount", "sum")
).sort_values("Units_Sold", ascending=False)

print(product_sales.head(10))

# 13. State-wise analysis
print("\n6. TOP 10 STATES BY RECORDED AMOUNT")

state_sales = df.groupby("ship-state").agg(
    Recorded_Amount=("Amount", "sum"),
    Units=("Qty", "sum"),
    Unique_Orders=("Order ID", "nunique")
).sort_values("Recorded_Amount", ascending=False)

print(state_sales.head(10))

print("\nAnalysis completed successfully!")



























