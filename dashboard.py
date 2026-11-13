#python -m streamlit run dashboard.py -->to run this file
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/Amazon Sale Report.csv",
        low_memory=False
    )

    # Clean column names and unnecessary columns
    df.columns = df.columns.str.strip()
    df = df.drop(
        columns=["index", "Unnamed: 22"],
        errors="ignore"
    )

    # Clean data types
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%m-%d-%y",
        errors="coerce"
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"], errors="coerce"
    )

    df["Qty"] = pd.to_numeric(
        df["Qty"], errors="coerce"
    )

    df["Category"] = df["Category"].astype("string").str.strip().str.title()

    return df.drop_duplicates()


st.title("🛒 E-commerce Sales Dashboard")
st.caption("Explore your sales performance using interactive filters.")

try:
    df = load_data()

    # Sidebar filters
    st.sidebar.header("Dashboard Filters")

    categories = sorted(
        df["Category"].dropna().unique().tolist()
    )

    selected_categories = st.sidebar.multiselect(
        "Select product categories",
        categories,
        default=categories
    )

    statuses = sorted(
        df["Status"].dropna().unique().tolist()
    )

    selected_statuses = st.sidebar.multiselect(
        "Select order statuses",
        statuses,
        default=statuses
    )

    # Apply filters
    filtered_df = df[
        df["Category"].isin(selected_categories)
        & df["Status"].isin(selected_statuses)
    ].copy()

    st.subheader("Key Performance Indicators")

    # Calculate metrics from the filtered data
    total_sales = filtered_df["Amount"].sum(min_count=1)

    total_orders = filtered_df["Order ID"].nunique()

    total_quantity = filtered_df["Qty"].sum(min_count=1)

    # Average recorded amount per order with valid amounts
    valid_sales = filtered_df.dropna(
        subset=["Order ID", "Amount"]
    )

    order_amounts = valid_sales.groupby(
        "Order ID"
    )["Amount"].sum()

    average_order_value = (
        order_amounts.mean()
        if not order_amounts.empty
        else 0
    )

    # Display KPI cards
    col1, col2, col3, col4 = st.columns(4)

    sales_display = (
        f"₹{total_sales:,.2f}"
        if pd.notna(total_sales)
        else "N/A"
    )

    quantity_display = (
        f"{total_quantity:,.0f}"
        if pd.notna(total_quantity)
        else "N/A"
    )

    col1.metric("💰 Total Recorded Sales", sales_display)
    col2.metric("🛍️ Unique Orders", f"{total_orders:,}")
    col3.metric("📦 Quantity Recorded", quantity_display)
    col4.metric(
        "🧾 Average Order Value",
        f"₹{average_order_value:,.2f}"
    )

    st.divider()

    st.subheader("Dataset Overview")

    col1, col2 = st.columns(2)

    col1.metric("Filtered Records", f"{len(filtered_df):,}")

    missing_amounts = filtered_df["Amount"].isna().sum()
    col2.metric("Records Missing Amount", f"{missing_amounts:,}")

    with st.expander("View filtered data"):
        st.dataframe(
            filtered_df,
            use_container_width=True
        )

    # Download filtered data
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv_data,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(
        "Dataset not found. Please check that "
        "'data/Amazon Sale Report.csv' exists."
    )

except KeyError as error:
    st.error(
        f"A required column was not found: {error}. "
        "Please check your CSV column names."
    )
# ==========================================
    # INVENTORY AND SLOW-SELLING PRODUCT ALERTS
    # ==========================================

st.divider()
st.header("📦 Inventory & Sales Alerts")
st.caption(
    "Identify products that need restocking "
    "or may need help improving sales."
)
# Load current stock information
stock_df = pd.read_csv(
    "data/Sale Report.csv",
    low_memory=False
)
stock_df.columns = stock_df.columns.str.strip()
# Check required columns
if "SKU Code" not in stock_df.columns or "Stock" not in stock_df.columns:
    st.error(
        "Sale Report.csv must contain 'SKU Code' and 'Stock' columns."
    )
else:
    # Clean stock data
    stock_df["SKU Code"] = (
        stock_df["SKU Code"]
        .astype("string")
        .str.strip()
        .str.upper()
    )
    stock_df["Stock"] = pd.to_numeric(
        stock_df["Stock"], errors="coerce"
    )
    stock_df = stock_df.dropna(
        subset=["SKU Code", "Stock"]
    )
    stock_df = stock_df[
        stock_df["SKU Code"] != ""
    ]
    # Combine repeated stock records for each SKU
    stock_grouped = (
        stock_df.groupby("SKU Code", as_index=False)
        .agg(
            Available_Stock=("Stock", "sum"),
            Category=("Category", "first")
            if "Category" in stock_df.columns
            else ("SKU Code", "first")
        )
    )
    # Clean sales data
    sales_df = df.copy()
    sales_df["SKU"] = (
        sales_df["SKU"]
        .astype("string")
        .str.strip()
        .str.upper()
    )
    sales_df["Qty"] = pd.to_numeric(
        sales_df["Qty"], errors="coerce"
    )
    sales_df["Date"] = pd.to_datetime(
        sales_df["Date"], errors="coerce"
    )
    sales_df = sales_df.dropna(
        subset=["SKU", "Date", "Qty"]
    )
    sales_df = sales_df[sales_df["SKU"] != ""]
    # Find the latest date available in the dataset
    if sales_df.empty:
        st.warning("No valid dated sales records were found.")
    else:
        latest_date = sales_df["Date"].max().normalize()
        # User-adjustable alert settings
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        with alert_col1:
            stock_limit = st.number_input(
                "Low-stock threshold (units)",
                min_value=0,
                value=5,
                step=1
            )
        with alert_col2:
            sales_days = st.selectbox(
                "Sales analysis period",
                [7, 30, 90],
                index=1,
                format_func=lambda x: f"Last {x} days"
            )
        with alert_col3:
            slow_sales_limit = st.number_input(
                "Slow-sales threshold (units)",
                min_value=0,
                value=5,
                step=1
            )
        # Use the dataset's latest date as the reference date
        period_start = (
            latest_date - pd.Timedelta(days=sales_days - 1)
        )
        period_sales = sales_df[
            (sales_df["Date"] >= period_start)
            & (sales_df["Date"] < latest_date + pd.Timedelta(days=1))
        ]
        # Calculate units sold by SKU in the selected period
        sales_summary = (
            period_sales.groupby("SKU", as_index=False)
            .agg(Units_Sold=("Qty", "sum"))
        )
        # Identify SKUs that have any historical sales record
        historical_skus = set(sales_df["SKU"].unique())
        # Match stock and sales using SKU codes
        inventory = stock_grouped.merge(
            sales_summary,
            left_on="SKU Code",
            right_on="SKU",
            how="left"
        )
        inventory["Has_Sales_History"] = (
            inventory["SKU Code"].isin(historical_skus)
        )
        # Missing period sales are zero only for SKUs
        # that have some sales history in the dataset
        inventory["Units_Sold"] = inventory[
            "Units_Sold"
        ].fillna(0)
        inventory["Stock_Alert"] = (
            inventory["Available_Stock"] <= stock_limit
        )
        inventory["Slow_Sales_Alert"] = (
            inventory["Has_Sales_History"]
            & (inventory["Units_Sold"] <= slow_sales_limit)
        )
        # Generate alert messages
        def make_alert(row):
            messages = []
            if row["Available_Stock"] <= 0:
                messages.append("OUT OF STOCK - Restock immediately")
            elif row["Stock_Alert"]:
                messages.append("LOW STOCK - Consider restocking")
            if row["Slow_Sales_Alert"]:
                messages.append(
                    "SLOW SELLING - Review promotion or pricing"
                )
            if not row["Has_Sales_History"]:
                messages.append(
                    "NO MATCHING SALES HISTORY - Check SKU"
                )
            return " | ".join(messages) if messages else "Stock and sales OK"
        inventory["Alert"] = inventory.apply(
            make_alert, axis=1
        )
        # KPI summary
        low_stock_count = int(inventory["Stock_Alert"].sum())
        slow_sales_count = int(
            inventory["Slow_Sales_Alert"].sum()
        )
        unmatched_count = int(
            (~inventory["Has_Sales_History"]).sum()
        )
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("⚠️ Low-stock products", low_stock_count)
        kpi2.metric("📉 Slow-selling products", slow_sales_count)
        kpi3.metric("❓ No sales history", unmatched_count)
        st.caption(
            f"Sales period: {period_start.date()} to "
            f"{latest_date.date()} "
            f"(based on the latest date in your dataset)."
        )
        # Display products requiring attention
        # Display products requiring attention
alert_products = inventory[
    inventory["Stock_Alert"]
    | inventory["Slow_Sales_Alert"]
    | (~inventory["Has_Sales_History"])
].copy()

st.subheader("🚨 Products Requiring Attention")

if alert_products.empty:
    st.success("No products triggered the selected alert rules.")
else:
    # Sort by alert priority without relying on missing columns
    alert_products["Priority"] = (
        alert_products["Available_Stock"].le(0).astype(int) * 4
        + alert_products["Stock_Alert"].astype(int) * 2
        + alert_products["Slow_Sales_Alert"].astype(int)
    )

    alert_products = alert_products.sort_values(
        by="Priority",
        ascending=False
    )

    st.dataframe(
        alert_products[
            [
                "SKU Code",
                "Category",
                "Available_Stock",
                "Units_Sold",
                "Alert"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    alert_csv = alert_products.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Inventory Alerts",
        data=alert_csv,
        file_name="inventory_alerts.csv",
        mime="text/csv"
    )
            # Download the alerts report
    alert_csv = alert_products.to_csv(
        index=False
    ).encode("utf-8")
    st.download_button(
        "⬇️ Download Inventory Alerts",
        data=alert_csv,
        file_name="inventory_alerts.csv",
        mime="text/csv",
        key="download_inventory_alerts"
    )
# ==========================================
# STATE-WISE DEMAND & GROWTH RECOMMENDATIONS
# ==========================================

st.divider()
st.header("📍 State-wise Demand & Growth Recommendations")

st.write(
    "Analyze historical orders by state and product category "
    "to identify potential growth opportunities."
)

# Check whether required columns are available
required_columns = [
    "ship-state", "Category", "Order ID", "Qty", "Amount"
]

missing_columns = [
    col for col in required_columns
    if col not in filtered_df.columns
]

if missing_columns:
    st.warning(
        f"Required columns are missing: {', '.join(missing_columns)}"
    )
else:
    # Prepare a separate copy for this analysis
    demand_df = filtered_df.copy()

    demand_df["ship-state"] = (
        demand_df["ship-state"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    demand_df["Category"] = (
        demand_df["Category"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    demand_df["Qty"] = pd.to_numeric(
        demand_df["Qty"], errors="coerce"
    )

    demand_df["Amount"] = pd.to_numeric(
        demand_df["Amount"], errors="coerce"
    )

    # Remove records without state or category
    demand_df = demand_df.dropna(
        subset=["ship-state", "Category"]
    )

    demand_df = demand_df[
        (demand_df["ship-state"] != "")
        & (demand_df["Category"] != "")
    ]

    if demand_df.empty:
        st.info("No valid state and category records are available.")
    else:
        # ------------------------------------------
        # 1. State ranking by unique orders
        # ------------------------------------------
        st.subheader("🏆 States with the Most Orders")

        state_summary = (
            demand_df.groupby("ship-state")
            .agg(
                Unique_Orders=("Order ID", "nunique"),
                Units_Sold=("Qty", "sum"),
                Recorded_Amount=("Amount", "sum")
            )
            .sort_values("Unique_Orders", ascending=False)
            .reset_index()
        )

        st.bar_chart(
            state_summary.head(10).set_index("ship-state")[
                ["Unique_Orders"]
            ]
        )

        st.dataframe(
            state_summary.head(10),
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------------------
        # 2. Select a state for category analysis
        # ------------------------------------------
        st.subheader("🛍️ Product Demand by State")

        available_states = sorted(
            demand_df["ship-state"].unique().tolist()
        )

        selected_state = st.selectbox(
            "Choose a state",
            available_states,
            key="growth_selected_state"
        )

        state_df = demand_df[
            demand_df["ship-state"] == selected_state
        ].copy()

        category_summary = (
            state_df.groupby("Category")
            .agg(
                Unique_Orders=("Order ID", "nunique"),
                Units_Sold=("Qty", "sum"),
                Recorded_Amount=("Amount", "sum")
            )
            .sort_values("Unique_Orders", ascending=False)
            .reset_index()
        )

        st.write(
            f"Product categories with the most orders in "
            f"**{selected_state}**:"
        )

        st.bar_chart(
            category_summary.head(10).set_index("Category")[
                ["Unique_Orders"]
            ]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------------------
        # 3. Growth recommendations
        # ------------------------------------------
        st.subheader("💡 Potential Growth Opportunities")

        top_categories = category_summary.head(3)

        if top_categories.empty:
            st.info("No category results are available for this state.")
        else:
            for _, row in top_categories.iterrows():
                st.success(
                    f"Consider testing more products in "
                    f"**{row['Category']}** in **{selected_state}**. "
                    f"It recorded {row['Unique_Orders']:,.0f} unique "
                    f"orders and {row['Units_Sold']:,.0f} units sold."
                )

            st.caption(
                "These are opportunities based on historical order "
                "volume, not guaranteed future demand. Check stock, "
                "profit margins, and customer feedback before expanding."
            )

        # ------------------------------------------
        # 4. Recorded amount per unit
        # ------------------------------------------
        st.subheader("💰 Pricing Analysis")

        price_df = state_df[
            (state_df["Qty"] > 0)
            & (state_df["Amount"].notna())
            & (state_df["Amount"] >= 0)
        ].copy()

        if price_df.empty:
            st.info(
                "There is not enough valid quantity and amount data "
                "to calculate recorded amount per unit."
            )
        else:
            price_summary = (
                price_df.groupby("Category")
                .agg(
                    Total_Units=("Qty", "sum"),
                    Total_Recorded_Amount=("Amount", "sum")
                )
                .reset_index()
            )

            price_summary["Recorded_Amount_Per_Unit"] = (
                price_summary["Total_Recorded_Amount"]
                / price_summary["Total_Units"]
            )

            price_summary = price_summary.sort_values(
                "Recorded_Amount_Per_Unit",
                ascending=False
            )

            st.write(
                "Compare the average recorded amount per unit "
                "for categories in the selected state."
            )

            st.bar_chart(
                price_summary.set_index("Category")[
                    ["Recorded_Amount_Per_Unit"]
                ]
            )

            st.dataframe(
                price_summary,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Recorded amount per unit is total recorded Amount "
                "divided by total Qty. It is not necessarily the "
                "listed price or profit per product."
            )

        # ------------------------------------------
        # 5. Download the state analysis
        # ------------------------------------------
        state_csv = category_summary.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download State Category Analysis",
            data=state_csv,
            file_name="state_category_analysis.csv",
            mime="text/csv",
            key="download_state_category_analysis"
        )