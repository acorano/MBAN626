import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="MBAN626 Retail Dashboard", layout="wide")

st.title("Global Retail Sales Performance Dashboard")
st.markdown("Interactive dashboard based on the Superstore dataset with live USD to PHP conversion.")

@st.cache_data
def load_data():
    df = pd.read_csv("Superstore.csv", encoding="latin1")

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["MonthName"] = df["Order Date"].dt.month_name()

    df.rename(columns={
        "Sales": "sales",
        "Profit": "profit",
        "Quantity": "quantity"
    }, inplace=True)

    return df

df = load_data()

st.sidebar.header("Filters")

selected_region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + sorted(df["Region"].dropna().unique().tolist())
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All"] + sorted(df["Category"].dropna().unique().tolist())
)

filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

st.subheader("Live Currency Conversion")

rate = None
total_sales_usd = filtered_df["sales"].sum()
total_sales_php = None

try:
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=10)
    data = response.json()

    if response.status_code == 200 and "rates" in data and "PHP" in data["rates"]:
        rate = data["rates"]["PHP"]
        total_sales_php = total_sales_usd * rate
    else:
        st.warning("Could not retrieve exchange rate.")
except Exception:
    st.warning("API request failed.")

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales (USD)", f"${total_sales_usd:,.2f}")

if rate is not None:
    col2.metric("USD to PHP Rate", f"{rate:,.4f}")
    col3.metric("Total Sales (PHP)", f"₱{total_sales_php:,.2f}")
else:
    col2.metric("USD to PHP Rate", "Unavailable")
    col3.metric("Total Sales (PHP)", "Unavailable")

if rate is not None:
    currency_df = pd.DataFrame({
        "Currency": ["USD", "PHP"],
        "Total Sales": [total_sales_usd, total_sales_php]
    })

    fig_currency = px.bar(
        currency_df,
        x="Currency",
        y="Total Sales",
        text="Total Sales",
        title="Live Currency Conversion of Total Sales"
    )
    fig_currency.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
    st.plotly_chart(fig_currency, use_container_width=True)

st.subheader("Sales by Category by Region")

category_region = (
    filtered_df.groupby(["Region", "Category"])["sales"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    category_region,
    x="Category",
    y="sales",
    color="Category",
    animation_frame="Region",
    title="Sales (USD) by Category by Region",
    labels={"sales": "Sales (USD)"}
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Profit by Region")

region_profit = (
    filtered_df.groupby("Region")["profit"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    region_profit,
    x="Region",
    y="profit",
    color="Region",
    title="Profit (USD) by Region",
    labels={"profit": "Profit (USD)"}
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Monthly Sales Trend")

monthly_sales = (
    filtered_df.groupby("Month")["sales"]
    .sum()
    .reset_index()
)

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="sales",
    markers=True,
    title="Monthly Sales (USD) Trend",
    labels={"sales": "Sales (USD)"}
)
fig3.update_layout(hovermode="x unified")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Top 10 Products by Sales")

top_products = (
    filtered_df.groupby("Product Name")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x="sales",
    y="Product Name",
    orientation="h",
    text="sales",
    title="Top 10 Products by Sales (USD)",
    labels={"sales": "Sales (USD)", "Product Name": "Product Name"}
)
fig4.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
fig4.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig4, use_container_width=True)