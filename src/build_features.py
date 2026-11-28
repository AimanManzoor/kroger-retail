"""Build chronological repeat-purchase feature snapshots from local retail data."""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
LOOKBACK = 180
HORIZON = 30

QUERY = """
WITH historical AS (
    SELECT
        household_key,
        PRODUCT_ID,
        COUNT(DISTINCT BASKET_ID) AS purchase_frequency,
        SUM(QUANTITY) AS total_quantity,
        AVG(SALES_VALUE) AS average_spending,
        AVG(ABS(RETAIL_DISC)) AS average_discount,
        MAX(DAY) AS last_purchase_day
    FROM transaction_data
    WHERE DAY <= ?
      AND DAY > ? - ?
      AND QUANTITY > 0
      AND household_key IS NOT NULL
      AND PRODUCT_ID IS NOT NULL
    GROUP BY household_key, PRODUCT_ID
),
future AS (
    SELECT DISTINCT household_key, PRODUCT_ID
    FROM transaction_data
    WHERE DAY > ?
      AND DAY <= ?
      AND QUANTITY > 0
)
SELECT
    h.*,
    ? - h.last_purchase_day AS recency,
    CAST(f.PRODUCT_ID IS NOT NULL AS INTEGER) AS target
FROM historical h
LEFT JOIN future f
    ON h.household_key = f.household_key
    AND h.PRODUCT_ID = f.PRODUCT_ID
"""


def main():
    with duckdb.connect(
        str(PROCESSED / "retail.duckdb"), read_only=True
    ) as con:
        min_day, max_day = con.execute(
            "SELECT MIN(DAY), MAX(DAY) FROM transaction_data"
        ).fetchone()

        if min_day is None or max_day - min_day + 1 < LOOKBACK + 3 * HORIZON:
            raise ValueError("Insufficient history for three chronological snapshots.")

        snapshots = {
            "train": max_day - 3 * HORIZON,
            "validation": max_day - 2 * HORIZON,
            "test": max_day - HORIZON,
        }

        for name, cutoff in snapshots.items():
            df = con.execute(
                QUERY,
                [cutoff, cutoff, LOOKBACK, cutoff, cutoff + HORIZON, cutoff],
            ).df()

            if df.empty or df["target"].nunique() != 2:
                raise ValueError(f"{name}: expected nonempty data with both target classes.")
            if df.duplicated(["household_key", "PRODUCT_ID"]).any():
                raise ValueError(f"{name}: duplicate household-product pairs.")

            df.to_parquet(PROCESSED / f"{name}_features.parquet", index=False)

            print(f"{name}: cutoff={cutoff}, records={len(df):,}, "
                  f"repurchase rate={df['target'].mean():.2%}")


if __name__ == "__main__":
    main()
