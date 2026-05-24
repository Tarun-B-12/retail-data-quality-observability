import duckdb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
from datetime import datetime
from src.store_results import get_run_history, get_latest_checks, DB_PATH

def generate_trend_chart(output_path: str = "outputs/trend_chart.png"):
    """Generate a health score trend chart from run history."""
    
    history = get_run_history()
    
    if not history:
        print("No run history found.")
        return None
    
    run_ids = [r["run_id"] for r in history]
    scores = [r["health_score"] for r in history]
    timestamps = [r["run_timestamp"][:10] for r in history]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(run_ids, scores, marker="o", linewidth=2.5,
            color="#2563EB", markersize=8, markerfacecolor="white",
            markeredgewidth=2.5)
    
    # Fill area under line
    ax.fill_between(run_ids, scores, alpha=0.1, color="#2563EB")
    
    # Add score labels above each point
    for rid, score, ts in zip(run_ids, scores, timestamps):
        ax.annotate(f"{score}",
                    xy=(rid, score),
                    xytext=(0, 12),
                    textcoords="offset points",
                    ha="center",
                    fontsize=10,
                    fontweight="bold",
                    color="#1e40af")
    
    # Reference lines
    ax.axhline(y=95, color="#16a34a", linestyle="--",
               alpha=0.5, linewidth=1, label="Target (95)")
    ax.axhline(y=80, color="#dc2626", linestyle="--",
               alpha=0.5, linewidth=1, label="Alert threshold (80)")
    
    ax.set_xlabel("Run ID", fontsize=11)
    ax.set_ylabel("Health Score", fontsize=11)
    ax.set_title("Data Quality Health Score Over Time", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.set_xticks(run_ids)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Trend chart saved to {output_path}")
    return output_path

def generate_html_report(output_path: str = "outputs/quality_report.html"):
    """Generate a full HTML quality report."""
    
    history = get_run_history()
    
    if not history:
        print("No run history found.")
        return None
    
    latest = history[-1]
    run_id = latest["run_id"]
    checks = get_latest_checks(run_id)
    
    passed_checks = [c for c in checks if c["status"] == "PASS"]
    failed_checks = [c for c in checks if c["status"] == "FAIL"]
    
    score = latest["health_score"]
    score_color = "#16a34a" if score >= 90 else "#d97706" if score >= 75 else "#dc2626"
    
    # Build checks table rows
    check_rows = ""
    for c in checks:
        status_badge = (
            '<span style="background:#dcfce7;color:#166534;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">PASS</span>'
            if c["status"] == "PASS" else
            '<span style="background:#fee2e2;color:#991b1b;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">FAIL</span>'
        )
        failure_info = (
            f"{c['failure_count']:,} rows ({c['failure_pct']}%)"
            if c["status"] == "FAIL" else "None"
        )
        check_rows += f"""
        <tr>
            <td style="padding:10px 14px">{c['check_name']}</td>
            <td style="padding:10px 14px;text-align:center">{status_badge}</td>
            <td style="padding:10px 14px;color:#6b7280">{failure_info}</td>
            <td style="padding:10px 14px;color:#6b7280;font-size:13px">{c['note'] or ''}</td>
        </tr>"""
    
    # Build history table rows
    history_rows = ""
    for r in history:
        sc = r["health_score"]
        sc_color = "#16a34a" if sc >= 90 else "#d97706" if sc >= 75 else "#dc2626"
        history_rows += f"""
        <tr>
            <td style="padding:10px 14px">{r['run_id']}</td>
            <td style="padding:10px 14px">{r['run_timestamp'][:19].replace('T', ' ')}</td>
            <td style="padding:10px 14px">{r['total_rows']:,}</td>
            <td style="padding:10px 14px">{r['passed']}/{r['total_checks']}</td>
            <td style="padding:10px 14px;font-weight:700;color:{sc_color}">{sc}</td>
        </tr>"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Data Quality Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background:#f8fafc; color:#1e293b; margin:0; padding:32px; }}
  .container {{ max-width:900px; margin:0 auto; }}
  h1 {{ font-size:28px; font-weight:700; margin-bottom:4px; }}
  .subtitle {{ color:#64748b; margin-bottom:32px; font-size:14px; }}
  .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px; }}
  .card {{ background:white; border-radius:12px; padding:20px;
           box-shadow:0 1px 3px rgba(0,0,0,0.08); }}
  .card-label {{ font-size:12px; color:#64748b; font-weight:600;
                 text-transform:uppercase; letter-spacing:0.05em; }}
  .card-value {{ font-size:28px; font-weight:700; margin-top:6px; }}
  .section {{ background:white; border-radius:12px; padding:24px;
              box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:24px; }}
  h2 {{ font-size:16px; font-weight:700; margin:0 0 16px 0; }}
  table {{ width:100%; border-collapse:collapse; }}
  th {{ text-align:left; padding:10px 14px; font-size:12px; font-weight:600;
        text-transform:uppercase; color:#64748b; border-bottom:2px solid #e2e8f0; }}
  tr:nth-child(even) {{ background:#f8fafc; }}
  img {{ width:100%; border-radius:8px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Data Quality Report</h1>
  <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
     Dataset: Online Retail II | Run ID: {run_id}</p>

  <div class="cards">
    <div class="card">
      <div class="card-label">Health Score</div>
      <div class="card-value" style="color:{score_color}">{score}</div>
    </div>
    <div class="card">
      <div class="card-label">Total Rows</div>
      <div class="card-value">{latest['total_rows']:,}</div>
    </div>
    <div class="card">
      <div class="card-label">Checks Passed</div>
      <div class="card-value" style="color:#16a34a">{latest['passed']}</div>
    </div>
    <div class="card">
      <div class="card-label">Checks Failed</div>
      <div class="card-value" style="color:#dc2626">{latest['failed']}</div>
    </div>
  </div>

  <div class="section">
    <h2>Health Score Trend</h2>
    <img src="trend_chart.png" alt="Health Score Trend">
  </div>

  <div class="section">
    <h2>Validation Results (Latest Run)</h2>
    <table>
      <thead>
        <tr>
          <th>Check</th><th style="text-align:center">Status</th>
          <th>Failures</th><th>Notes</th>
        </tr>
      </thead>
      <tbody>{check_rows}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>Run History</h2>
    <table>
      <thead>
        <tr>
          <th>Run ID</th><th>Timestamp</th><th>Rows</th>
          <th>Checks Passed</th><th>Health Score</th>
        </tr>
      </thead>
      <tbody>{history_rows}</tbody>
    </table>
  </div>
</div>
</body>
</html>"""
    
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"HTML report saved to {output_path}")
    return output_path
