from pathlib import Path
import duckdb

con = duckdb.connect()

for path in sorted(Path("data/raw").rglob("*.csv")):

    print(f"\n{'=' * 60}")
    print(f"DATASET: {path.name}")
    print("=" * 60)

    source = f"read_csv_auto('{str(path).replace(chr(39), chr(39)*2)}')"

    count = con.execute(
        f"SELECT COUNT(*) FROM {source}"
    ).fetchone()[0]

    print(f"Total records: {count:,}")

    schema = con.execute(
        f"DESCRIBE SELECT * FROM {source}"
    ).df()

    print(f"Total columns: {len(schema)}")

    print("\nData quality summary:")

    summary = con.execute(
        f"SUMMARIZE SELECT * FROM {source}"
    ).df()

    print(summary.to_string(index=False))

con.close()
