from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent

def build_agent(db_uri, llm_name="openai:gpt-4.1", top_k=25):
    llm = init_chat_model(llm_name)
    db = SQLDatabase.from_uri(db_uri)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    system_prompt = f"""
    You are an agent designed to interact with a PostgreSQL database. 
    Given an input question, create a syntactically correct {db.dialect} query to run,
    then look at the results of the query and return the answer. Unless the user
    specifies a specific number of examples they wish to obtain, always limit your
    query to at most {top_k} results.

    You can order the results by a relevant column to return the most interesting
    examples in the database. Never query for all the columns from a specific table,
    only ask for the relevant columns given the question.

    You MUST double check your query before executing it. If you get an error while
    executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
    database.

    To start you should ALWAYS look at the tables in the database to see what you
    can query. Do NOT skip this step.

    Then you should query the schema of the most relevant tables.
    
    After getting the query results, always show **all rows** from the result up to the limit of {top_k}. Do not summarize or omit rows unless explicitly instructed.
    
    Output your answer in human natural language in an easy and readable way.
    """

    agent = create_react_agent(llm, tools, prompt=system_prompt)
    print("sql agent is built!")
    return agent
