# Data Quality Anomaly Explanations

Generated: 2026-05-24T00:51:48.477879

Health Score: 90.0/100

Failures Found: 1

---

## Price non-negative

**Status:** FAIL

**Rows Affected:** 5 (0.0%)

**Explanation:**

# Data Quality Issue: Negative Prices Detected

We've found 5 transactions in your dataset where the price is showing as negative, which shouldn't be possible in normal retail operations. While this only affects a tiny fraction of your data (0.0005%), even a few incorrect prices can skew sales totals, revenue reports, and profitability analysis if they go unnoticed. These bad records could also cause problems downstream if they're used in automated reports or dashboards.

**My recommendation:** We should investigate these 5 transactions to understand why they occurred—whether they're refunds that were miscoded, data entry errors, or system glitches—and then correct them before finalizing any financial reporting for this period.

---
