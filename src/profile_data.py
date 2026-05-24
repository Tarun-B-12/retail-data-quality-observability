import pandas as pd

def profile_dataframe(df: pd.DataFrame) -> dict:
    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": {}
    }
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = round(null_count / len(df) * 100, 2)
        col_profile = {
            "dtype": str(df[col].dtype),
            "null_count": int(null_count),
            "null_pct": null_pct,
            "unique_count": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_profile["min"] = float(df[col].min())
            col_profile["max"] = float(df[col].max())
            col_profile["mean"] = round(float(df[col].mean()), 2)
            negative_count = int((df[col] < 0).sum())
            col_profile["negative_count"] = negative_count
            col_profile["negative_pct"] = round(negative_count / len(df) * 100, 2)
        profile["columns"][col] = col_profile
    return profile
