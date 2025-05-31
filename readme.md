# ExplainDB

ExplainDB is a Flask-based web application that allows users to query structured databases using natural language and automatically receive visualizations, natural language explanations, and full answers. The platform integrates GPT and the LIDA visualization engine to provide a seamless data exploration and understanding experience, especially for non-technical users.

## Project Overview

ExplainDB combines natural language processing, database querying, and data visualization in the following automated workflow:

1. **Generate SQL queries based on user questions**  
2. **Execute the queries and clean the result data**  
3. **Use the GPT-4.1 model to refine the query result and generate a natural language answer**  
4. **Automatically generate additional data exploration goals relevant to the user's question**  
5. **Use LIDA to generate visualizations and explanations**  
6. **Display a main chart and multiple recommended charts, each accompanied by a natural language explanation to help users understand the visualized data**  
7. **Support multi-turn conversations and session history to allow follow-up questions and reviews**

This platform provides an intuitive, all-in-one data exploration experience for users who may not be familiar with SQL or data visualization tools.

Refer to `ExplainDB - Example.html` for an example of input and output.

## Project Structure

```
├── app.py                   # Main Flask application
├── core.py                  # Core logic: querying, visualization, explanation
├── agent/                   # LangChain agent building and execution
│   ├── agent_builder.py/    # LangChain agent builder
│   ├── agent_runner.py/     # LangChain agent execution
│   └── call_gpt.py/         # Get GPT response
├── lida/                    # Modified LIDA visualization engine
├── templates/               # HTML templates for the UI
├── flask_session_data/      # Session data storage (on disk)
├── json_output/             # JSON cache of query results
├── requirements.txt         # Python dependencies
├── data_schema_overview     # Explanation of the data schema
├── ExplainDB - Example.html # Example input and output
├── ExplainDB - Example_files/ # Example supporting files. Do not move.
└── README.md                # This documentation
```

## System Architecture

ExplainDB consists of the following key modules working together to provide end-to-end natural language query explanation and visualization:

1. **Architecture Diagram**

```
[ User Browser ]
       |
       v
[ Flask Frontend (HTML/JS) ]
       |
       v
[ Flask Backend (app.py) ]
       |
       v
[ process_query() in core.py ]
       |
       |---> [ LangChain Agent ]
       |         |
       |         v
       |    [ SQL Query Generator ]
       |         |
       |         v
       |    [ SQL Execution ]
       |
       |---> [ GPT-4.1 ]
       |         |
       |         v
       |    [ Header Refinement / Explanation Rewrite ]
       |
       |---> [ LIDA (Modified) ]
       |         |
       |         v
       |    [ Goal Generation, Chart Rendering, Explanation ]
       |
       v
[ Final Output: Answer + Charts + Explanations ]
```

2. **Component Overview**

**Frontend (HTML + JavaScript):**

Provides the user interface for entering questions and viewing visualizations and explanations.

**Flask Backend:**

Manages routing (/, /ask, /clear_history) and user session state.

Delegates query handling to the core.py module.

LangChain Agent: Generates and executes SQL queries based on the natural language input.

**GPT-4.1:**

Cleans and refines SQL result headers.

Rewrites raw explanations into human-friendly text.

**LIDA (Modified):**

Analyzes data and generates related exploration goals.

Creates visualizations using matplotlib.

Provides code and structured explanation blocks.

Session Storage: Stores user interactions and charts for history review.



## Installation & Setup

### Install Dependencies

Make sure you are using Python 3.8 or above. Then install the required packages with:

```bash
pip install -r requirements.txt
```

### Configure OpenAI API Key

This project uses the GPT-4.1 model from OpenAI. You must set your API key as an environment variable:

```bash
# macOS / Linux
export OPENAI_API_KEY=your_api_key_here

# Windows (CMD)
set OPENAI_API_KEY=your_api_key_here
```

### Run the Application

```bash
python app.py
```

Then open your browser and go to:  
`http://127.0.0.1:5000/`

## Database Support and Extension

The project includes two example databases by default:

- `Chinook`: A classic SQLite music store database  
- `Northwind`: A PostgreSQL-based order and customer management database

You can add more databases by editing the `DATABASES` variable in `app.py`:

```python
DATABASES = {
    "Chinook": "sqlite:///Chinook.db",
    "Northwind": "postgresql+psycopg2://user:password@localhost:your_host/northwind",
    "MyCustomDB": "sqlite:///path/to/your.db"
}
```

Connection strings should follow SQLAlchemy's standard format.



## Notes on LIDA Integration

This project incorporates [LIDA](https://github.com/microsoft/lida), a visualization tool by Microsoft. However, **we do not import LIDA as a package directly**. Instead, we have **modified the source code** to enable the following enhancements:

- Higher-resolution image generation
- Chart layout and styling optimized for web display
- Overall improvement of user experience

Modifications are located in the `lida/components/` directory.


# Data Schema Overview

This document outlines the core data structures and flow used in the ExplainDB system.

## 1. Input: Natural Language Query

Users provide a natural language question along with a selected database. For example:

```
"Which 10 genres are the most popular by sales volume, and what is the average price per track in each?"
```

## 2. Processing Pipeline

The `process_query()` function returns the following structure:

| Key               | Type       | Description                                  |
| ----------------- | ---------- | -------------------------------------------- |
| final_answer      | str        | Final natural language response to the query |
| json_result       | List[Dict] | Cleaned SQL result processed by GPT          |
| goals             | List[str]  | Exploration goals generated by LIDA          |
| chart_code_list   | List[str]  | Code snippets for chart generation           |
| chart_base64_list | List[str]  | Base64-encoded PNG images of the charts      |
| explanation_list  | List[str]  | User-friendly explanations for the charts    |
| trace_log         | List[str]  | SQL reasoning process trace                  |
| df                | DataFrame  | Final processed DataFrame                    |

## 3. Intermediate Structures

- DataFrame: Constructed from SQL result, refined via GPT, and used by LIDA for analysis.
- chart_code_list / chart_base64_list / explanation_list: Aligned by index and derived per goal.

## 4. Session History (Flask)

User history is tracked in a Flask session.

## 5. Supported Databases

Configured via SQLAlchemy URIs:
The system is database-agnostic. Additional databases can be added via the DATABASES config, assuming they are SQLAlchemy-compatible.

```python
DATABASES = {
    "Chinook": "sqlite:///Chinook.db",
    "Northwind": "postgresql+psycopg2://..."
}
```

## 6. Output Files

- `json_output/output.json`: JSON result after GPT processing
- `flask_session_data/`: Session state stored on disk

## Summary

ExplainDB processes natural language queries against structured databases using LLMs and visualization tools. It relies on session memory, in-memory DataFrames, and dynamic generation of charts and explanations for each user question.

````

````
