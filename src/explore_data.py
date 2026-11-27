from pathlib import Path
import pandas as pd

files = sorted(Path("data/raw").rglob("*.csv"))

for path in files:
    print("\n" + "=" * 70)
    print(f"DATASET: {path.name}")
    print("=" * 70)

    df = pd.read_csv(path, nrows=5)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five records:")
    print(df.to_string(index=False))

    print("\nInferred sample data types:")
    print(df.dtypes)
