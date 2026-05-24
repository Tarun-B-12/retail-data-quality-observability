# Data Quality Anomaly Explanations

Generated: 2026-05-24T00:47:09.508121

Health Score: 90.0/100

Failures Found: 1

---

## Price non-negative

**Status:** FAIL

**Rows Affected:** 5 (0.0%)

**Explanation:**

# Data Quality Issue: Negative Prices Detected

**What's happening:** Our transaction data contains 5 records where the price field shows a negative value instead of a positive dollar amount. While this represents less than 0.01% of our dataset, it indicates these transactions were recorded incorrectly—likely data entry errors, refunds coded as new sales, or system glitches.

**Why this matters:** Even a small number of negative prices can skew financial reports, inventory analysis, and revenue calculations. If someone runs a quick total on transaction value without catching this, we could misreport sales figures or make decisions based on incomplete information.

**What to do:** I recommend we immediately investigate these 5 records to determine their root cause—whether they're refunds that should be marked differently, system errors, or something else—then correct them before publishing any reports. Going forward, we should implement an automated check that flags negative prices before data enters our system so this doesn't happen again.

---
