from pathlib import Path

import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(
    page_title="Retail Intelligence Lab",
    layout="wide"
)

st.title("Retail Intelligence Lab")
st.caption("Retail Analytics | Machine Learning | Decision Intelligence")

DB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data/processed/retail.duckdb"
)

@st.cache_data(ttl=300)
def query(sql, params=None):
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(sql, params or []).df()

departments = query("""
    SELECT DISTINCT DEPARTMENT
    FROM retail_sales
    WHERE DEPARTMENT IS NOT NULL
    ORDER BY DEPARTMENT
""")

department = st.sidebar.selectbox(
    "Select Department",
    ["All Departments"] + departments["DEPARTMENT"].tolist()
)

where = ""
params = []

if department != "All Departments":
    where = "WHERE DEPARTMENT = ?"
    params = [department]

kpis = query(f"""
    SELECT
        SUM(SALES_VALUE) AS revenue,
        COUNT(DISTINCT household_key) AS households,
        COUNT(DISTINCT BASKET_ID) AS baskets,
        COUNT(DISTINCT PRODUCT_ID) AS products
    FROM retail_sales
    {where}
""", params)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Sales", f"${kpis.revenue.iloc[0]:,.2f}")
c2.metric("Households", f"{kpis.households.iloc[0]:,}")
c3.metric("Baskets", f"{kpis.baskets.iloc[0]:,}")
c4.metric("Products", f"{kpis.products.iloc[0]:,}")

weekly = query(f"""
    SELECT WEEK_NO, SUM(SALES_VALUE) AS revenue
    FROM retail_sales
    {where}
    GROUP BY WEEK_NO
    ORDER BY WEEK_NO
""", params)

st.plotly_chart(
    px.line(
        weekly,
        x="WEEK_NO",
        y="revenue",
        title="Weekly Sales Trends"
    ),
    use_container_width=True
)

categories = query(f"""
    SELECT
        COMMODITY_DESC,
        SUM(SALES_VALUE) AS revenue
    FROM retail_sales
    {where}
    GROUP BY COMMODITY_DESC
    ORDER BY revenue DESC
    LIMIT 15
""", params)

st.plotly_chart(
    px.bar(
        categories,
        x="revenue",
        y="COMMODITY_DESC",
        orientation="h",
        title="Top 15 Product Categories"
    ),
    use_container_width=True
)

st.subheader("Machine Learning Pipelines")

st.info("""
Coming next:
- Purchase probability predictions
- Personalized product recommendations
- Customer segmentation
- Demand forecasting
- Explainable AI
""")
