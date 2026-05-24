import anthropic
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def explain_failure(check_name: str, failure_count: int, failure_pct: float, 
                    total_rows: int, note: str = "") -> str:
    """Use Claude to explain a validation failure in plain English."""
    
    prompt = f"""You are a data quality analyst explaining an issue to a business stakeholder.

A data validation check failed on a retail transactions dataset with {total_rows:,} rows.

Failed check: {check_name}
Failure count: {failure_count:,} rows affected
Failure percentage: {failure_pct}% of total data
Additional context: {note if note else 'None'}

Write a short explanation (3-5 sentences) that covers:
1. What the problem is in plain English
2. Why it matters for business reporting or analysis
3. One concrete recommendation to fix or handle it

Do not use technical jargon. Write as if explaining to a finance or operations manager."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def explain_all_failures(validation_results: dict) -> dict:
    """Generate explanations for all failed checks."""
    
    failures = [e for e in validation_results["expectations"] if not e["passed"]]
    
    if not failures:
        return {
            "run_timestamp": validation_results["run_timestamp"],
            "health_score": validation_results["health_score"],
            "failures_found": 0,
            "explanations": [],
            "summary": "No validation failures found. Dataset passed all quality checks."
        }
    
    print(f"Generating explanations for {len(failures)} failed check(s)...")
    
    explanations = []
    for check in failures:
        print(f"  Explaining: {check['name']}...")
        explanation = explain_failure(
            check_name=check["name"],
            failure_count=check.get("failure_count", 0),
            failure_pct=check.get("failure_pct", 0.0),
            total_rows=validation_results["total_rows"],
            note=check.get("note", "")
        )
        explanations.append({
            "check_name": check["name"],
            "status": "FAIL",
            "failure_count": check.get("failure_count", 0),
            "failure_pct": check.get("failure_pct", 0.0),
            "explanation": explanation
        })
    
    return {
        "run_timestamp": validation_results["run_timestamp"],
        "health_score": validation_results["health_score"],
        "failures_found": len(failures),
        "explanations": explanations
    }

def save_explanation_report(explanation_results: dict, output_path: str = "outputs/anomaly_explanations.md"):
    """Save explanations to a markdown file."""
    
    lines = []
    lines.append("# Data Quality Anomaly Explanations")
    lines.append(f"\nGenerated: {explanation_results['run_timestamp']}")
    lines.append(f"\nHealth Score: {explanation_results['health_score']}/100")
    lines.append(f"\nFailures Found: {explanation_results['failures_found']}")
    lines.append("\n---\n")
    
    if explanation_results["failures_found"] == 0:
        lines.append(explanation_results.get("summary", "No failures found."))
    else:
        for item in explanation_results["explanations"]:
            lines.append(f"## {item['check_name']}")
            lines.append(f"\n**Status:** FAIL")
            lines.append(f"\n**Rows Affected:** {item['failure_count']:,} ({item['failure_pct']}%)")
            lines.append(f"\n**Explanation:**\n\n{item['explanation']}")
            lines.append("\n---\n")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    print(f"Explanation report saved to {output_path}")
    return output_path
