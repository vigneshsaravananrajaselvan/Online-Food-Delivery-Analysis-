import streamlit as st

st.title("🍔 Online Food Delivery Dashboard")
st.write("Dashboard is starting...")


import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
# PAGE CONFIGURATION---------------------------------
st.set_page_config(
    page_title="Online Food Delivery Dashboard",
    page_icon="🍔",
    layout="wide"
)
#LOAD MYSQL CREDENTIALS-----------------------------------
load_dotenv()
username = "root"
password = os.getenv("MYSQL_PASSWORD")
host = "localhost"
port = 3306
database = "food_delivery_db"
if not password:
    st.error("MYSQL_PASSWORD was not found in the .env file.")
    st.stop()
# MYSQL CONNECTION---------------------------
@st.cache_resource
def get_engine():
    return create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    )
engine = get_engine()

#LOAD DATA--------------------------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM food_delivery_orders"
    return pd.read_sql(query, engine)
try:
    df = load_data()
except Exception as e:
    st.error(f"Could not connect to MySQL: {e}")
    st.stop()
# TITLE----------------------------------------
st.title("🍔 Online Food Delivery Analysis Dashboard")
st.markdown(
    "Data-driven business insights from online food delivery orders"
)
st.divider()
#SIDEBAR FILTERS------------------------------
st.sidebar.header("Dashboard Filters")
# City filter-------------------------------------------
cities = sorted(df["City"].dropna().unique())
selected_cities = st.sidebar.multiselect(
    "Select City",
    cities,
    default=cities
)
# Cuisine filter------------------------------------------
cuisines = sorted(df["Cuisine_Type"].dropna().unique())
selected_cuisines = st.sidebar.multiselect(
    "Select Cuisine",
    cuisines,
    default=cuisines
)
# Payment filter-----------------------
payment_modes = sorted(df["Payment_Mode"].dropna().unique())
selected_payment_modes = st.sidebar.multiselect(
    "Select Payment Mode",
    payment_modes,
    default=payment_modes
)
#APPLY FILTERS---------------------------------
filtered_df = df[
    (df["City"].isin(selected_cities)) &
    (df["Cuisine_Type"].isin(selected_cuisines)) &
    (df["Payment_Mode"].isin(selected_payment_modes))
].copy()
#KPI CALCULATIONS---------------------------
total_orders = len(filtered_df)
total_revenue = filtered_df["Final_Amount"].sum()
average_order_value = filtered_df["Final_Amount"].mean()
average_delivery_time = filtered_df["Delivery_Time_Min"].mean()
cancellation_rate = (
    (filtered_df["Order_Status"] == "Cancelled").mean() * 100
)
average_delivery_rating = filtered_df["Delivery_Rating"].mean()
profit_margin = filtered_df["Profit_Margin_Pct"].mean()
#KPI CARDS----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Total Orders",
    f"{total_orders:,}"
)
col2.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)
col3.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}"
)
col4.metric(
    "Average Delivery Time",
    f"{average_delivery_time:.2f} min"
)

col5, col6, col7 = st.columns(3)
col5.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%"
)
col6.metric(
    "Average Delivery Rating",
    f"{average_delivery_rating:.2f} / 5"
)
col7.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)
st.divider()
#MONTHLY REVENUE--------------------
st.subheader("📈 Monthly Revenue")
monthly_revenue = (
    filtered_df
    .dropna(subset=["Order_Date"])
    .assign(
        Month=lambda x: pd.to_datetime(x["Order_Date"]).dt.to_period("M").astype(str)
    )
    .groupby("Month")["Final_Amount"]
    .sum()
    .reset_index()
)
monthly_revenue = monthly_revenue.set_index("Month")
st.line_chart(
    monthly_revenue["Final_Amount"]
)
#CITY PERFORMANCE---------------------
st.subheader("🏙️ Revenue by City")
city_revenue = (
    filtered_df
    .groupby("City")["Final_Amount"]
    .sum()
    .sort_values(ascending=False)
)
st.bar_chart(city_revenue)
#CUISINE PERFORMANCE----------------------
st.subheader("🍜 Revenue by Cuisine")
cuisine_revenue = (
    filtered_df
    .groupby("Cuisine_Type")["Final_Amount"]
    .sum()
    .sort_values(ascending=False)
)
st.bar_chart(cuisine_revenue)
#PAYMENT MODE---------------------------------------
st.subheader("💳 Orders by Payment Mode")
payment_orders = (
    filtered_df
    .groupby("Payment_Mode")
    .size()
    .sort_values(ascending=False)
)
st.bar_chart(payment_orders)
#ORDER STATUS--------------------------------------------
st.subheader("📦 Order Status")
order_status = (
    filtered_df
    .groupby("Order_Status")
    .size()
    .sort_values(ascending=False)
)
st.bar_chart(order_status)
#CANCELLATION REASONS-----------------------------
st.subheader("❌ Cancellation Reasons")
cancelled_df = filtered_df[
    filtered_df["Order_Status"] == "Cancelled"
]
cancellation_reasons = (
    cancelled_df
    .groupby("Cancellation_Reason")
    .size()
    .sort_values(ascending=False)
)
st.bar_chart(cancellation_reasons)
#DELIVERY TIME BY CITY----------------------------------
st.subheader("🚴 Average Delivery Time by City")
delivery_city = (
    filtered_df
    .groupby("City")["Delivery_Time_Min"]
    .mean()
    .sort_values(ascending=False)
)
st.bar_chart(delivery_city)
# PEAK HOUR ANALYSIS-------------------
st.subheader("🕐 Peak Hour Demand")
peak_hour = (
    filtered_df
    .groupby("Peak_Hour_Indicator")
    .size()
)
peak_hour.index = peak_hour.index.map({
    0: "Non-Peak",
    1: "Peak"
})
st.bar_chart(peak_hour)
#RESTAURANT PERFORMANCE-------------------------------
st.subheader("🏪 Top 10 Restaurants by Revenue")
restaurant_revenue = (
    filtered_df
    .groupby("Restaurant_Name")["Final_Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(restaurant_revenue)
#FOOTER--------------------------------
st.divider()
st.caption(
    "Online Food Delivery Analysis | Python • SQL • MySQL • Pandas • Streamlit"
)