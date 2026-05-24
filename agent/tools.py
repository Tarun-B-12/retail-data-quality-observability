import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.load_data import load_retail_data
from src.profile_data import profile_dataframe
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
                    "description": "Path to the Excel file"
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
    }
]

_state = {"df": None}

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "load_data":
        filepath = tool_input.get("filepath", "data/raw/online_retail_II.xlsx")
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
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
