import pandas as pd
from datetime import datetime

def run_validation_suite(df: pd.DataFrame) -> dict:
    """Run data quality validation suite on the retail dataframe."""
    
    results = {
        "run_timestamp": datetime.now().isoformat(),
        "total_rows": len(df),
        "expectations": []
    }
    
    def add_check(name, passed, failure_count=None, failure_pct=None, note=None):
        entry = {
            "name": name,
            "passed": bool(passed),
            "status": "PASS" if passed else "FAIL"
        }
        if failure_count is not None:
            entry["failure_count"] = int(failure_count)
        if failure_pct is not None:
            entry["failure_pct"] = round(float(failure_pct), 2)
        if note:
            entry["note"] = note
        results["expectations"].append(entry)

    # 1. Invoice not null
    fc = df["Invoice"].isnull().sum()
    add_check("Invoice not null", fc == 0, fc, fc / len(df) * 100)

    # 2. StockCode not null
    fc = df["StockCode"].isnull().sum()
    add_check("StockCode not null", fc == 0, fc, fc / len(df) * 100)

    # 3. Quantity not null
    fc = df["Quantity"].isnull().sum()
    add_check("Quantity not null", fc == 0, fc, fc / len(df) * 100)

    # 4. Price not null
    fc = df["Price"].isnull().sum()
    add_check("Price not null", fc == 0, fc, fc / len(df) * 100)

    # 5. Price non-negative
    fc = (df["Price"] < 0).sum()
    add_check("Price non-negative", fc == 0, fc, fc / len(df) * 100)

    # 6. Customer ID null rate below 25%
    null_pct = df["Customer ID"].isnull().sum() / len(df) * 100
    add_check(
        "Customer ID null rate below 25%",
        null_pct < 25,
        df["Customer ID"].isnull().sum(),
        null_pct,
        note=f"Actual null rate: {round(null_pct, 2)}%"
    )

    # 7. Country not null
    fc = df["Country"].isnull().sum()
    add_check("Country not null", fc == 0, fc, fc / len(df) * 100)

    # 8. InvoiceDate not null
    fc = df["InvoiceDate"].isnull().sum()
    add_check("InvoiceDate not null", fc == 0, fc, fc / len(df) * 100)

    # 9. Row count above 500k
    add_check("Row count above 500k", len(df) > 500000,
              note=f"Actual row count: {len(df):,}")

    # 10. Column count equals 8
    add_check("Column count equals 8", len(df.columns) == 8,
              note=f"Actual column count: {len(df.columns)}")

    passed = sum(1 for e in results["expectations"] if e["passed"])
    failed = len(results["expectations"]) - passed

    results["total_checks"] = len(results["expectations"])
    results["passed"] = passed
    results["failed"] = failed
    results["health_score"] = round(passed / len(results["expectations"]) * 100, 1)

    return results
