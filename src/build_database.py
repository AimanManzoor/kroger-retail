from pathlib import Path
import duckdb

Path("data/processed").mkdir(parents=True, exist_ok=True)

con = duckdb.connect("data/processed/retail.duckdb")

for path in sorted(Path("data/raw").rglob("*.csv")):
    table = path.stem
    print(f"Loading {table}...")

    con.execute(
        f'CREATE OR REPLACE TABLE "{table}" AS '
        'SELECT * FROM read_csv_auto(?)',
        [str(path)]
    )

    count = con.execute(
        f'SELECT COUNT(*) FROM "{table}"'
    ).fetchone()[0]

    print(f"{table}: {count:,} records")

print("\nAvailable tables:")
print(con.execute("SHOW TABLES").df())

con.close()
