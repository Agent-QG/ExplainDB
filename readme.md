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
    "Northwind": "postgresql+psycopg2://user:password@localhost:5432/northwind",
    "MyCustomDB": "sqlite:///path/to/your.db"
}
```

Connection strings should follow SQLAlchemy's standard format.

## Project Structure

```
├── app.py                  # Main Flask application
├── core.py                 # Core logic: querying, visualization, explanation
├── agent/					# LangChain agent building and execution
│   ├── agent_builder.py/	# LangChain agent builder
│   ├── agent_runner.py/	# LangChain agent execution
│   └── call_gpt.py/		# Get GPT response
├── lida/                   # Modified LIDA visualization engine
├── templates/              # HTML templates for the UI
├── flask_session_data/     # Session data storage (on disk)
├── json_output/            # JSON cache of query results
├── requirements.txt        # Python dependencies
└── README.md               # This documentation
```

## Notes on LIDA Integration

This project incorporates [LIDA](https://github.com/microsoft/lida), a visualization tool by Microsoft. However, **we do not import LIDA as a package directly**. Instead, we have **modified the source code** to enable the following enhancements:

- Higher-resolution image generation
- Chart layout and styling optimized for web display
- Overall improvement of user experience

Modifications are located in the `lida/components/` directory.