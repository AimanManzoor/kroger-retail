import duckdb

con = duckdb.connect(
    "data/processed/retail.duckdb",
    read_only=True
)

queries = {
    "Business Overview": """
        SELECT
            ROUND(SUM(SALES_VALUE), 2) AS total_sales,
            COUNT(DISTINCT household_key) AS households,
            COUNT(DISTINCT BASKET_ID) AS baskets,
            COUNT(DISTINCT PRODUCT_ID) AS products
        FROM retail_sales
    """,

    "Top Performing Departments": """
        SELECT
            DEPARTMENT,
            ROUND(SUM(SALES_VALUE), 2) AS revenue,
            SUM(QUANTITY) AS units_sold
        FROM retail_sales
        GROUP BY DEPARTMENT
        ORDER BY revenue DESC
        LIMIT 10
    """,

    "Weekly Sales Trends": """
        SELECT
            WEEK_NO,
            ROUND(SUM(SALES_VALUE), 2) AS revenue
        FROM retail_sales
        GROUP BY WEEK_NO
        ORDER BY WEEK_NO
    """,

    "Customer Purchase Behaviour": """
        SELECT
            household_key,
            COUNT(DISTINCT BASKET_ID) AS visits,
            ROUND(SUM(SALES_VALUE), 2) AS spending,
            COUNT(DISTINCT PRODUCT_ID) AS unique_products
        FROM retail_sales
        GROUP BY household_key
        ORDER BY spending DESC
        LIMIT 10
    """
}

for title, query in queries.items():
    print(f"\n--- {title} ---")
    print(con.execute(query).df().to_string(index=False))

con.close()
