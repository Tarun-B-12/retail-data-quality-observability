import pandas as pd

def load_retail_data(filepath: str) -> pd.DataFrame:
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
    print(f"Loaded {len(df):,} rows.")
    return df
