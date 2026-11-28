import duckdb

con = duckdb.connect(
    "data/processed/retail.duckdb",
    read_only=True
)

queries = {
    "Total transaction records": """
        SELECT COUNT(*) FROM transaction_data
    """,

    "Unique households": """
        SELECT COUNT(DISTINCT household_key)
        FROM transaction_data
    """,

    "Unique baskets": """
        SELECT COUNT(DISTINCT BASKET_ID)
        FROM transaction_data
    """,

    "Unique purchased products": """
        SELECT COUNT(DISTINCT PRODUCT_ID)
        FROM transaction_data
    """,

    "Duplicate product identifiers": """
        SELECT COUNT(*)
        FROM (
            SELECT PRODUCT_ID
            FROM product
            GROUP BY PRODUCT_ID
            HAVING COUNT(*) > 1
        ) AS duplicates
    """,

    "Transactions without matching products": """
        SELECT COUNT(*)
        FROM transaction_data t
        LEFT JOIN product p
            ON t.PRODUCT_ID = p.PRODUCT_ID
        WHERE p.PRODUCT_ID IS NULL
    """,

    "Negative quantities": """
        SELECT COUNT(*)
        FROM transaction_data
        WHERE QUANTITY < 0
    """,

    "Missing household identifiers": """
        SELECT COUNT(*)
        FROM transaction_data
        WHERE household_key IS NULL
    """
}

for name, query in queries.items():
    result = con.execute(query).fetchone()[0]
    print(f"{name}: {result:,}")

con.close()
