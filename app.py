import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("Global Retail Sales Performance Dashboard")
st.write("Interactive dashboard for sales, profit, products, and live currency conversion.")

@st.cache_data
def load_data():
    df = pd.read_csv("Superstore.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["MonthName"] = df["Order Date"].dt.month_name()
    df = df.rename(columns={
        "Sales": "sales",
        "Profit": "profit",
        "Quantity": "quantity"
    })
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

selected_region = st.sidebar.selectbox(
    "Region", ["All"] + sorted(df["Region"].dropna().unique().tolist())
)

selected_category = st.sidebar.selectbox(
    "Category", ["All"] + sorted(df["Category"].dropna().unique().tolist())
)

filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# Live exchange rate
rate = None
try:
    response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
    data = response.json()

    if response.status_code == 200 and "rates" in data and "PHP" in data["rates"]:
        rate = data["rates"]["PHP"]
except Exception:
    rate = None

total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
total_quantity = filtered_df["quantity"].sum()

# KPI metrics
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales (USD)", f"${total_sales:,.2f}")
col2.metric("Total Profit (USD)", f"${total_profit:,.2f}")
col3.metric("Total Quantity", f"{int(total_quantity):,}")

if rate is not None:
    col4.metric("USD → PHP Rate", f"{rate:,.4f}")
    col5.metric("Total Sales (PHP)", f"₱{total_sales * rate:,.2f}")
else:
    col4.metric("USD → PHP Rate", "Unavailable")
    col5.metric("Total Sales (PHP)", "Unavailable")

# Chart 1: Sales by Category
sales_by_category = filtered_df.groupby("Category", as_index=False)["sales"].sum()

fig1 = px.bar(
    sales_by_category,
    x="Category",
    y="sales",
    color="Category",
    title="Sales by Category (USD)"
)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Profit by Region
profit_by_region = filtered_df.groupby("Region", as_index=False)["profit"].sum()

fig2 = px.bar(
    profit_by_region,
    x="Region",
    y="profit",
    color="Region",
    title="Profit by Region (USD)"
)

st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Monthly Sales Trend
monthly_sales = filtered_df.groupby("Month", as_index=False)["sales"].sum()

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="sales",
    markers=True,
    title="Monthly Sales Trend (USD)"
)

fig3.update_layout(hovermode="x unified")

st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Top 10 Products by Sales
top_products = (
    filtered_df.groupby("Product Name", as_index=False)["sales"]
    .sum()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig4 = px.bar(
    top_products,
    x="sales",
    y="Product Name",
    orientation="h",
    text="sales",
    title="Top 10 Products by Sales (USD)"
)

fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig4.update_layout(yaxis=dict(categoryorder="total ascending"))

st.plotly_chart(fig4, use_container_width=True)
