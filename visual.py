import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load and clean the dataset
df = pd.read_csv(
    "data/Amazon Sale Report.csv",
    low_memory=False
)

df = df.drop(
    columns=["index", "Unnamed: 22"],
    errors="ignore"
)

df.columns = df.columns.str.strip()
df = df.drop_duplicates()

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m-%d-%y",
    errors="coerce"
)

df["Category"] = df["Category"].str.strip().str.title()

# Create output folder
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

# 1. Monthly Recorded Amount - Pie Chart

df["Month"] = df["Date"].dt.to_period("M")

monthly_sales = df.groupby("Month")["Amount"].sum()

# Remove missing and non-positive amounts for the pie chart
monthly_sales = monthly_sales.dropna()
monthly_sales = monthly_sales[monthly_sales > 0]

plt.figure(figsize=(9, 9))

plt.pie(
    monthly_sales.values,
    labels=monthly_sales.index.astype(str),
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Monthly Recorded Amount - 2022")
plt.tight_layout()
plt.savefig(output_dir / "monthly_sales.png")
plt.show()

# 2. Top product categories by quantity
category_sales = (
    df[df["Qty"] > 0]
    .groupby("Category")["Qty"]
    .sum()
    .sort_values()
)

plt.figure(figsize=(10, 6))
category_sales.plot(kind="barh")
plt.title("Product Demand by Category")
plt.xlabel("Recorded Units")
plt.ylabel("Category")
plt.tight_layout()
plt.savefig(output_dir / "category_demand.png")
plt.show()


# 3. Order Distribution - Bar Graph

status_counts = df["Status"].value_counts().sort_values(ascending=False)

plt.figure(figsize=(12, 6))

ax = status_counts.plot(kind="bar")

plt.title("Order Distribution by Status", fontsize=16)
plt.xlabel("Order Status", fontsize=12)
plt.ylabel("Number of Records", fontsize=12)
plt.xticks(rotation=45, ha="right")

# Display values above each bar
ax.bar_label(ax.containers[0], fmt="%.0f", padding=3)

plt.tight_layout()
plt.savefig(output_dir / "order_status.png", dpi=300)
plt.show()

# 4. Top 10 States by Recorded Amount - Colourful Horizontal Bar Chart

state_sales = (
    df.groupby("ship-state")["Amount"]
    .sum()
    .dropna()
    .nlargest(10)
    .sort_values(ascending=True)
)

plt.figure(figsize=(12, 7))

colors = plt.cm.tab10(range(len(state_sales)))

ax = state_sales.plot(
    kind="barh",
    color=colors,
    edgecolor="black"
)

plt.title("Top 10 States by Recorded Amount", fontsize=16)
plt.xlabel("Recorded Amount (INR)", fontsize=12)
plt.ylabel("State", fontsize=12)

# Display amount values at the end of each bar
ax.bar_label(
    ax.containers[0],
    fmt="%.0f",
    padding=5
)

plt.tight_layout()
plt.savefig(output_dir / "state_sales.png", dpi=300)
plt.show()