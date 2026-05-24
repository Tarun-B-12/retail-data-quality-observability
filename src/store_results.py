import duckdb
import json
from datetime import datetime

DB_PATH = "outputs/quality_results.duckdb"

def init_db():
    """Create tables if they don't exist."""
    con = duckdb.connect(DB_PATH)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS quality_runs (
            run_id        INTEGER PRIMARY KEY,
            run_timestamp VARCHAR,
            total_rows    INTEGER,
            total_checks  INTEGER,
            passed        INTEGER,
            failed        INTEGER,
            health_score  DOUBLE
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS quality_checks (
            check_id      INTEGER PRIMARY KEY,
            run_id        INTEGER,
            check_name    VARCHAR,
            passed        BOOLEAN,
            status        VARCHAR,
            failure_count INTEGER,
            failure_pct   DOUBLE,
            note          VARCHAR
        )
    """)
    
    con.close()

def store_run(validation_results: dict) -> int:
    """Store a validation run and return the run_id."""
    init_db()
    con = duckdb.connect(DB_PATH)
    
    # Get next run_id
    result = con.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM quality_runs").fetchone()
    run_id = result[0]
    
    # Insert run summary
    con.execute("""
        INSERT INTO quality_runs VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        run_id,
        validation_results["run_timestamp"],
        validation_results["total_rows"],
        validation_results["total_checks"],
        validation_results["passed"],
        validation_results["failed"],
        validation_results["health_score"]
    ])
    
    # Insert individual checks
    for i, check in enumerate(validation_results["expectations"]):
        con.execute("""
            INSERT INTO quality_checks VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id * 100 + i,
            run_id,
            check["name"],
            check["passed"],
            check["status"],
            check.get("failure_count", 0),
            check.get("failure_pct", 0.0),
            check.get("note", "")
        ])
    
    con.close()
    print(f"Stored run {run_id} with health score {validation_results['health_score']}")
    return run_id

def get_run_history() -> list:
    """Retrieve all past runs for trend analysis."""
    init_db()
    con = duckdb.connect(DB_PATH)
    
    rows = con.execute("""
        SELECT run_id, run_timestamp, total_rows, total_checks, 
               passed, failed, health_score
        FROM quality_runs
        ORDER BY run_id ASC
    """).fetchall()
    
    con.close()
    
    history = []
    for row in rows:
        history.append({
            "run_id": row[0],
            "run_timestamp": row[1],
            "total_rows": row[2],
            "total_checks": row[3],
            "passed": row[4],
            "failed": row[5],
            "health_score": row[6]
        })
    
    return history

def get_latest_checks(run_id: int) -> list:
    """Retrieve individual checks for a specific run."""
    con = duckdb.connect(DB_PATH)
    
    rows = con.execute("""
        SELECT check_name, status, failure_count, failure_pct, note
        FROM quality_checks
        WHERE run_id = ?
        ORDER BY check_id ASC
    """, [run_id]).fetchall()
    
    con.close()
    
    checks = []
    for row in rows:
        checks.append({
            "check_name": row[0],
            "status": row[1],
            "failure_count": row[2],
            "failure_pct": row[3],
            "note": row[4]
        })
    
    return checks
