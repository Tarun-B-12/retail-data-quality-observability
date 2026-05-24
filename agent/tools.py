import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.load_data import load_retail_data
from src.profile_data import profile_dataframe
from src.run_validations import run_validation_suite
from src.store_results import store_run, get_run_history
import json

TOOL_DEFINITIONS = [
    {
        "name": "load_data",
        "description": "Load the retail dataset from the raw data folder. Returns confirmation and row count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the CSV file"
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "profile_data",
        "description": "Generate a full data quality profile of the loaded dataset. Returns null rates, data types, value ranges, and negative value counts per column.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "run_validations",
        "description": "Run the validation suite against the loaded dataset. Returns pass/fail results for each check and an overall health score out of 100.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "store_results",
        "description": "Store the validation results into the DuckDB quality results database for historical tracking. Call this after run_validations. Returns the run_id.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_run_history",
        "description": "Retrieve all past validation runs from the database to show health score trends over time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

_state = {"df": None, "validation_results": None}

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
        profile = profile_dataframe(_state["df"])
        return json.dumps(profile)

    elif tool_name == "run_validations":
        if _state["df"] is None:
            return json.dumps({"error": "No data loaded. Call load_data first."})
        results = run_validation_suite(_state["df"])
        _state["validation_results"] = results
        return json.dumps(results)

    elif tool_name == "store_results":
        if _state["validation_results"] is None:
            return json.dumps({"error": "No validation results found. Call run_validations first."})
        run_id = store_run(_state["validation_results"])
        return json.dumps({"status": "success", "run_id": run_id})

    elif tool_name == "get_run_history":
        history = get_run_history()
        return json.dumps({"runs": history, "total_runs": len(history)})

    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
