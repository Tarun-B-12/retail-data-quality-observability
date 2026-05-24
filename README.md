# Retail Data Quality and Observability Pipeline

## One-Line Summary
An agent-orchestrated data quality monitoring pipeline that profiles, validates, explains anomalies in plain English, and tracks data health over time across a 1M+ row retail dataset.

## Business Problem
Most data teams find out their data is broken when a dashboard is wrong or a stakeholder asks a question that cannot be answered. This pipeline catches data issues proactively by running automated validation checks, storing health scores over time, and using an LLM to explain failures in plain English so business stakeholders can act on them immediately.

## Target Stakeholder
Data Engineering leads, Analytics Managers, and business stakeholders who need to trust the data feeding their dashboards and reports.

## Tools Used
- Python
- Anthropic Claude API (Haiku) for anomaly explanations
- DuckDB for results storage and run history
- Great Expectations (validation framework)
- pandas for data profiling
- matplotlib for trend visualization
- GitHub for version control

## Dataset
Source: UCI Online Retail II Dataset (via Kaggle)
1,067,371 transactions across 8 columns covering invoices, products, quantities, prices, customers, and countries.

Notes:
- Public, anonymized retail transaction data
- Two years of order history across 43 countries
- Contains realistic data quality issues used for validation

## Agent Architecture
This project uses an agentic pipeline where Claude orchestrates 9 tools autonomously to complete the full quality check workflow.

```text
User Goal
    |
    v
[ Orchestrator Agent (Claude Haiku) ]
    |
    |-- load_data tool
    |-- profile_data tool
    |-- run_validations tool
    |-- store_results tool (DuckDB)
    |-- explain_failures tool (Claude API)
    |-- save_report tool (markdown)
    |-- generate_trend_chart tool (PNG)
    |-- generate_html_report tool (HTML)
    |-- get_run_history tool
    |
    v
Final Business Report
```

The agent decides the sequence and calls each tool based on results from the previous step. No manual sequencing required.

## Validation Suite (10 checks)
| Check | Type | Threshold |
|---|---|---|
| Invoice not null | Completeness | 0 nulls |
| StockCode not null | Completeness | 0 nulls |
| Quantity not null | Completeness | 0 nulls |
| Price not null | Completeness | 0 nulls |
| Price non-negative | Validity | 0 negative values |
| Customer ID null rate below 25% | Threshold | Max 25% nulls |
| Country not null | Completeness | 0 nulls |
| InvoiceDate not null | Completeness | 0 nulls |
| Row count above 500k | Volume | Min 500,000 rows |
| Column count equals 8 | Schema | Exactly 8 columns |

## KPIs
| KPI | Definition | Why It Matters |
|---|---|---|
| Health Score | % of checks passed per run | Single trackable number for stakeholders |
| Null Rate by Column | % of nulls per field | Catches upstream pipeline breaks |
| Failure Count | Rows failing any check | Measures unusable data volume |
| Health Score Trend | Score across multiple runs | Shows if quality is improving or degrading |

## Results (3 Validation Runs)
- Health Score: 90/100 (stable across all runs)
- Checks Passed: 9/10
- Failed Check: Price non-negative (5 rows, 0.0005%)
- Key Finding: 22.77% of transactions have no Customer ID (within threshold, likely guest purchases)

## Screenshots

### Health Score Trend
![Health Score Trend](images/data_quality_trend_chart.png)

### Validation Results and Run History
![Validation Results](images/data_quality_validation_results.png)

## How to Run

```bash
# Clone the repo
git clone https://github.com/Tarun-B-12/retail-data-quality-observability.git
cd retail-data-quality-observability

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# Add the dataset
# Download online_retail_II.csv from Kaggle and place in data/raw/

# Run the full pipeline
python agent/orchestrator.py
```

## Output Artifacts
- `outputs/quality_results.duckdb` - Run history database
- `outputs/anomaly_explanations.md` - LLM-generated failure explanations
- `outputs/trend_chart.png` - Health score trend visualization
- `outputs/quality_report.html` - Full HTML quality report

## What This Project Demonstrates
- AI agent design using tool calling and orchestration
- Data quality validation and observability pipeline engineering
- LLM integration for plain-English anomaly explanation
- DuckDB for lightweight analytical storage
- Trend tracking and historical run management
- Business-focused reporting from raw validation results
- Modular Python pipeline architecture

## Limitations
- Dataset is static (no live ingestion). Production version would connect to a live warehouse.
- Validation rules are hand-coded. Production version would support dynamic rule configuration.
- Single dataset. Architecture supports any tabular dataset with minimal changes.

## Next Improvements
- Add GitHub Actions to schedule pipeline runs automatically
- Add Slack or email alerts when health score drops below threshold
- Add column-level trend tracking (not just overall score)
- Connect to a live data warehouse (Snowflake, BigQuery, or Redshift)
- Add a Streamlit dashboard for real-time monitoring
