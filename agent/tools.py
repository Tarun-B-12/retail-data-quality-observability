import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.load_data import load_retail_data
from src.profile_data import profile_dataframe
from src.run_validations import run_validation_suite
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
        "description": "Run the Great Expectations validation suite against the loaded dataset. Returns pass/fail results for each expectation, failure counts, and an overall data health score out of 100.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

_state = {"df": None}

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
        return json.dumps(results)
    
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
