import anthropic
import json
import os
from dotenv import load_dotenv
from tools import TOOL_DEFINITIONS, execute_tool

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data quality analyst agent. Complete the full pipeline in order:
1. Load the dataset - filepath is always: data/raw/online_retail_II.csv
2. Run validations
3. Store results in the database
4. Explain any failed checks
5. Save the explanation report
6. Generate the trend chart
7. Generate the HTML report
8. Give a final summary

Be efficient. Use tools in sequence. Explain findings in business terms."""


def run_agent(user_goal: str):
    print("\n" + "="*60)
    print("AGENT STARTING")
    print("="*60)
    print(f"Goal: {user_goal}\n")

    messages = [{"role": "user", "content": user_goal}]
    step = 0

    while True:
        step += 1
        print(f"\n--- Agent Step {step} ---")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print("\n" + "="*60)
                    print("AGENT FINAL REPORT")
                    print("="*60)
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"Agent calling tool: {block.name}")
                    result = execute_tool(block.name, block.input)
                    print(f"Tool result preview: {result[:200]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

        if step >= 20:
            print("Max steps reached. Stopping.")
            break


if __name__ == "__main__":
    run_agent(
        "Run the complete data quality pipeline using file data/raw/online_retail_II.csv: "
        "load data, validate, store results, explain failures, save reports, "
        "generate trend chart and HTML report, then give me a full summary."
    )
