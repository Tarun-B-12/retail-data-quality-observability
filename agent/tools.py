import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.load_data import load_retail_data
from src.profile_data import profile_dataframe
from src.run_validations import run_validation_suite
from src.store_results import store_run, get_run_history
from src.explain_anomalies import explain_all_failures, save_explanation_report
import json

TOOL_DEFINITIONS = [
    {
        "name": "load_data",
        "description": "Load the retail dataset from the raw data folder. Returns confirmation and row count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the CSV file"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "profile_data",
        "description": "Generate a full data quality profile of the loaded dataset.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "run_validations",
        "description": "Run the validation suite against the loaded dataset. Returns pass/fail results and health score.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "store_results",
        "description": "Store validation results into DuckDB for historical tracking. Call after run_validations.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_run_history",
        "description": "Retrieve all past validation runs to show health score trends over time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "explain_failures",
        "description": "Use an LLM to generate plain-English explanations for all failed validation checks. Call after run_validations.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "save_report",
        "description": "Save the anomaly explanations to a markdown report file in the outputs folder.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

_state = {
    "df": None,
    "validation_results": None,
    "explanation_results": None
}

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "load_data":
        filepath = tool_input.get("filepath", "data/raw/online_retail_II.csv")
        df = load_retail_data(filepath)
        _state["df"] = df
        return json.dumps({
            "status": "success",
            "rows_loaded": len(df),
            "columns": list(df.columns)
        })

    elif tool_name == "profile_data":
        if _state["df"] is None:
            return json.dumps({"error": "No data loaded. Call load_data first."})
        return json.dumps(profile_dataframe(_state["df"]))

    elif tool_name == "run_validations":
        if _state["df"] is None:
            return json.dumps({"error": "No data loaded. Call load_data first."})
        results = run_validation_suite(_state["df"])
        _state["validation_results"] = results
        return json.dumps(results)

    elif tool_name == "store_results":
        if _state["validation_results"] is None:
            return json.dumps({"error": "No validation results. Call run_validations first."})
        run_id = store_run(_state["validation_results"])
        return json.dumps({"status": "success", "run_id": run_id})

    elif tool_name == "get_run_history":
        history = get_run_history()
        return json.dumps({"runs": history, "total_runs": len(history)})

    elif tool_name == "explain_failures":
        if _state["validation_results"] is None:
            return json.dumps({"error": "No validation results. Call run_validations first."})
        results = explain_all_failures(_state["validation_results"])
        _state["explanation_results"] = results
        return json.dumps({
            "failures_found": results["failures_found"],
            "explanations_generated": len(results["explanations"]),
            "preview": results["explanations"][0]["explanation"][:300] if results["explanations"] else "No failures"
        })

    elif tool_name == "save_report":
        if _state["explanation_results"] is None:
            return json.dumps({"error": "No explanations found. Call explain_failures first."})
        path = save_explanation_report(_state["explanation_results"])
        return json.dumps({"status": "success", "saved_to": path})

    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
