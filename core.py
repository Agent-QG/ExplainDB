import datetime
import json
import re
import time
from decimal import Decimal
from typing import Any

import pandas as pd
from llmx import llm

from agent.agent_builder import build_agent
from agent.agent_runner import ask_question
from agent.call_gpt import get_gpt_response
from lida.components import Manager
from lida.datamodel import TextGenerationConfig

# Initialize LLM (OpenAI) and LIDA Manager
text_gen = llm("openai")  # for openai
lida = Manager(text_gen=llm("openai", api_key=None))  # API key can be added
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-4.1", use_cache=True)

def process_query(
        db_uri="sqlite:///Chinook.db",
        llm_name="openai:gpt-4.1",
        question="Which 10 genres are the most popular by sales volume, and what is the average price per track in each?"
):
    """
    Main pipeline for:
    1. Querying the database via LangChain agent.
    2. Cleaning/parsing result into DataFrame.
    3. Using GPT to reformat headers.
    4. Generating summary, insights, visualizations, and explanations via LIDA.
    """

    agent = build_agent(db_uri, llm_name)
    trace_log, final_answer, search_result = ask_question(agent, question)
    print(final_answer)

    # Handle empty query result
    if not search_result:
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

    # Safely evaluate the search result into Python object
    eval_globals = {
        "__builtins__": {},
        "Decimal": Decimal,
        "datetime": datetime,
        "timezone": datetime.timezone,
        "timedelta": datetime.timedelta,
    }
    try:
        search_result = eval(search_result, eval_globals)
    except Exception as e:
        print("⚠️ Failed to parse search_result:", e)
        exit(1)

    df = pd.DataFrame(search_result)

    # Clean NaN std columns (avoid LIDA error)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].std() != df[col].std():  # NaN std check
                df[col] = df[col].fillna(0)

    # Save raw JSON
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    with open("json_output/output.json", "w", encoding="utf-8") as f:
        f.write(json_str)

    # Prepare GPT input for header refinement
    prompt = "You are a data analyst and json master. Please read the following JSON file and the user query process, and then complete the table headers for the JSON. Only output the new json content!"
    gpt_input = "This is json content:\n" + json_str + "\n//// This is user query process:\n" + "\n".join(
        map(str, trace_log))

    # Function: get cleaned JSON via GPT, retrying if needed
    def get_clean_json_from_gpt(prompt, gpt_input, max_retries=5):
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
            print(json_response)
            time.sleep(0.5)
        print("❌ Failed to extract valid JSON after max retries.")
        return None

    # Function: extract list of dicts from GPT output
    def extract_json_array(response_text):
        match = re.search(r'\[\s*{.*?}\s*]', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    # Get cleaned JSON output
    json_str_output = get_clean_json_from_gpt(prompt, gpt_input)
    data_list = json.loads(json_str_output)
    df = pd.DataFrame(data_list)

    # Parse datetime objects
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, datetime.datetime)).any():
            df[col] = pd.to_datetime(df[col])

    print(df)

    # Use LIDA to summarize the data
    summary = lida.summarize(df, textgen_config=textgen_config)
    print("summary got!!!!!!!")

    # Generate data exploration goals (questions)
    goals = lida.goals(summary, n=2)
    goals.insert(0, question)
    print("goals got!!!!!!!")

    # Generate visualizations and explanations for each goal
    chart_code_list = []
    chart_base64_list = []
    explanation_list = []

    for idx, goal in enumerate(goals):
        print(f"🚀 Generating chart for goal {idx + 1}")
        success = False
        for attempt in range(10):
            try:
                charts = lida.visualize(summary=summary, goal=goal, library="matplotlib")
                if charts:
                    chart = charts[0]
                    explanation_raw = lida.explain(code=chart.code)
                    explanation = " ".join(
                        item["explanation"]
                        for sublist in explanation_raw
                        for item in sublist
                        if isinstance(item, dict) and "explanation" in item
                    )

                    # Use GPT to rewrite explanation for end-users
                    prompt = (
                        "You are a data analyst and showing a figure to the user. "
                        "Read the following explanation generated by Lida about a chart. "
                        "Rewrite it into clear and fluent English that an average viewer of the chart can easily understand. "
                        "The rewritten explanation should help someone interpret the chart just by looking at it, without referring to any code. "
                        "It should be one coherent paragraph — not a list or bullet points. "
                        "Make the content informative but concise, avoiding unnecessary repetition. "
                        "Start the explanation with 'Explanation:' and end with 'Explanation end.'."
                    )
                    for i in range(10):
                        try:
                            response = get_gpt_response(prompt, explanation)
                            match = re.search(r'Explanation:.*?Explanation end\.', response, re.DOTALL)
                            if match:
                                extracted = match.group(0).strip()
                                print(f"✅ Explanation generated on attempt {i + 1}:\n")
                                break
                            else:
                                print(f"⚠️ Attempt {i + 1} failed to match Explanation. Retrying...")
                        except Exception as e:
                            print(f"⚠️ Attempt {i + 1} failed with error: {e}")
                        time.sleep(0.5)
                    else:
                        print("❌ All attempts failed to extract a valid Explanation.")

                    get_gpt_response(prompt, explanation)

                    chart_code_list.append(chart.code)
                    chart_base64_list.append(chart.raster)
                    explanation_list.append(explanation)
                    success = True
                    break
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed with error: {e}")
                time.sleep(0.2)

        if not success:
            print(f"⚠️ Failed to generate chart for goal {idx + 1}, inserting empty.")
            chart_code_list.append("")
            chart_base64_list.append("")
            explanation_list.append("")

    # Return all results for use in Flask or elsewhere
    return {
        "final_answer": final_answer,
        "json_result": data_list,
        "goals": goals,
        "chart_code_list": chart_code_list,
        "chart_base64_list": chart_base64_list,
        "explanation_list": explanation_list,
        "trace_log": trace_log,
        "df": df
    }

# Utility to format LIDA goal object
def format_goal(goal: Any) -> str:
    if isinstance(goal, str):
        return goal
    elif hasattr(goal, "question"):
        return str(goal.question)
    return str(goal)

# Utility to format LIDA explanation object
def format_explanation(expl: Any) -> str:
    if isinstance(expl, str):
        return expl
    try:
        lines = []
        for block in expl[0]:
            section = block.get('section', '')
            explanation = block.get('explanation', '')
            lines.append(f"[{section}] {explanation}")
        return "\n".join(lines)
    except Exception:
        return str(expl)
