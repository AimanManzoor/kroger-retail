import duckdb

con = duckdb.connect("data/processed/retail.duckdb")

con.execute("""
CREATE OR REPLACE VIEW retail_sales AS
SELECT
    t.household_key,
    t.BASKET_ID,
    t.DAY,
    t.WEEK_NO,
    t.PRODUCT_ID,
    t.STORE_ID,
    t.QUANTITY,
    t.SALES_VALUE,
    t.RETAIL_DISC,
    t.COUPON_DISC,
    p.DEPARTMENT,
    p.COMMODITY_DESC,
    p.BRAND
FROM transaction_data t
LEFT JOIN product p
    ON t.PRODUCT_ID = p.PRODUCT_ID
""")

print("Retail analytical view created.")

print(con.execute("""
    SELECT COUNT(*) AS records
    FROM retail_sales
""").df())

con.close()
