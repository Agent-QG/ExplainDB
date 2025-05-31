import datetime
import json
import re
import time
from decimal import Decimal
from typing import Any

import pandas as pd
#from lida import Manager, TextGenerationConfig, llm
from lida.components import Manager
from llmx import llm, TextGenerator
from lida.datamodel import Goal, Summary, TextGenerationConfig, Persona


from agent.agent_builder import build_agent
from agent.agent_runner import ask_question
from agent.call_gpt import get_gpt_response

text_gen = llm("openai")  # for openai

lida = Manager(text_gen=llm("openai", api_key=None))  # !! api key
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-4.1", use_cache=True)


def process_query(
        db_uri="sqlite:///Chinook.db",
        llm_name="openai:gpt-4.1",
        question="Which 10 genres are the most popular by sales volume, and what is the average price per track in each?"
):
    """
    Main function that:
    1. Sends a natural language query to the LangChain agent.
    2. Parses the SQL result into a DataFrame.
    3. Sends the JSON result and reasoning trace to GPT to get proper headers.
    4. Uses LIDA to summarize, generate goals, and visualize the data.
    5. Returns all useful intermediate and final results.

    This function can be called from a Flask route to return analysis results and chart base64 images for rendering.
    """
    agent = build_agent(db_uri, llm_name)

    # Get agent outputs: trace log, final natural language answer, and raw SQL query result
    trace_log, final_answer, search_result = ask_question(agent, question)

    print(final_answer)

    if not search_result:
        print("⚠️ No results found for the query.")
        return {
            "final_answer": "No data matched your query. Please try asking a different question.",
            "json_result": [],
            "goals": [],
            "chart_code_list": [],
            "chart_base64_list": [],
            "explanation_list": [],
            "trace_log": trace_log,
            "df": pd.DataFrame()
        }


    print("🔍 Raw search_result content:")
    print(search_result)

    eval_globals = {
        "__builtins__": {},
        "Decimal": Decimal,
        "datetime": datetime,
        "timezone": datetime.timezone,
        "timedelta": datetime.timedelta,
    }
    # Parse the raw search result (assumed to be stringified list of dicts)
    # Safe parsing of the SQL result (which may contain datetime, etc.)
    try:
        search_result = eval(search_result, eval_globals)
    except Exception as e:
        print("⚠️ Failed to parse search_result:", e)
        print("Raw content:", search_result)
        exit(1)

    # Convert result to DataFrame and save to JSON for debugging or GPT use
    df = pd.DataFrame(search_result)
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    with open("json_output/output.json", "w", encoding="utf-8") as f:
        f.write(json_str)

    # Prepare GPT prompt and input with the JSON data and query reasoning
    prompt = "You are a data analyst and json master. Please read the following JSON file and the user query process, and then complete the table headers for the JSON. Only output the new json content!"
    gpt_input = "This is json content:\n" + json_str + "\n//// This is user query process:\n" + "\n".join(
        map(str, trace_log))

    def get_clean_json_from_gpt(prompt, gpt_input, max_retries=100):
        """
        Calls GPT with retry logic until a valid JSON list is extracted.
        """
        for attempt in range(1, max_retries + 1):
            print(f"🔁 Attempt {attempt}...")
            json_response = get_gpt_response(prompt, gpt_input)
            clean_json_data = extract_json_array(json_response)

            if clean_json_data is not None:
                print("✅ Valid JSON extracted.")
                json_str_output = json.dumps(clean_json_data, indent=2, ensure_ascii=False)
                with open("json_output/output.json", "w", encoding="utf-8") as f:
                    f.write(json_str_output)
                return json_str_output

            print("❌ Invalid JSON format. Retrying...\n")
            time.sleep(0.5)

        print("❌ Failed to extract valid JSON after max retries.")
        return None

    def extract_json_array(response_text):
        """
        Regex + JSON parse to extract a list of dicts from raw GPT output.
        """
        match = re.search(r'\[\s*{.*?}\s*]', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    # Send to GPT to get cleaned headers
    json_str_output = get_clean_json_from_gpt(prompt, gpt_input)

    # Load back into DataFrame
    data_list = json.loads(json_str_output)
    df = pd.DataFrame(data_list)
    # Convert any datetime fields from raw `datetime` objects
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, datetime.datetime)).any():
            df[col] = pd.to_datetime(df[col])
    print("df got!!!!!!!")
    print(df)

    # Summarize data using LIDA
    summary = lida.summarize(df, textgen_config=textgen_config)
    print("summary got!!!!!!!")
    # Generate goals (data questions) automatically

    goals = lida.goals(summary, n=5)
    goals.insert(0, question)

    print("goals got!!!!!!!")
    # Generate initial chart based   on original query
    chart_code_list = []
    chart_base64_list = []
    explanation_list = []
    for idx, goal in enumerate(goals[:5]):
        try:
            print(f"🚀 Generating chart for goal {idx + 1}")
            print(goals[idx])

            charts = []
            for i in range(1, 101):
                charts = lida.visualize(summary=summary, goal=goal, library="matplotlib")
                if charts:
                    break

            if charts:
                chart = charts[0]
                explanation = lida.explain(code=chart.code)

                chart_code_list.append(chart.code)
                chart_base64_list.append(chart.raster)
                explanation_list.append(explanation)
            else:
                print(f"⚠️ No chart generated for goal {idx + 1}, inserting empty.")
                chart_code_list.append("")
                chart_base64_list.append("")
                explanation_list.append("")

        except Exception as e:
            print(f"❌ Error during visualization for goal {idx + 1}: {e}")
            chart_code_list.append("")
            chart_base64_list.append("")
            explanation_list.append("")
    # ✅ Return a dictionary with everything you need
    return {
        "final_answer": final_answer,  # Natural language answer to the original question
        "json_result": data_list,  # Structured JSON result of SQL query
        "goals": goals,  # Generated goals (alternative insights)
        "chart_code_list": chart_code_list,  # List of matplotlib code strings
        "chart_base64_list": chart_base64_list,  # List of base64 PNGs for direct HTML display
        "explanation_list": explanation_list,  # Explanation text for each chart
        "trace_log": trace_log,  # Reasoning + SQL generation trace
        "df": df  # Cleaned pandas DataFrame for further use
    }


"""
📝 How to use this function in a Flask app:

from flask import Flask, render_template

@app.route("/chart")
def show_charts():
    result = process_query(question="Which customers increased their total spending by at least 10% in 2010 compared to 2009")

    return render_template("chart.html", 
        final_answer=result["final_answer"],
        charts=result["chart_base64_list"],
        explanations=result["explanation_list"]
    )

🖼️ In your `chart.html`:
{% for chart, explanation in zip(charts, explanations) %}
    <img src="data:image/png;base64,{{ chart }}" alt="chart">
    <p>{{ explanation }}</p>
{% endfor %}

This way, your Flask app renders visual insights directly in HTML.
"""

def format_goal(goal: Any) -> str:
    if isinstance(goal, str):
        return goal
    elif hasattr(goal, "question"):
        return str(goal.question)
    return str(goal)


def format_explanation(expl: Any) -> str:
    if isinstance(expl, str):
        return expl
    try:
        # explanation is likely a list of dict sections
        lines = []
        for block in expl[0]:  # take the first explanation (explanation is [[{...}, {...}]]])
            section = block.get('section', '')
            explanation = block.get('explanation', '')
            lines.append(f"[{section}] {explanation}")
        return "\n".join(lines)
    except Exception:
        return str(expl)

