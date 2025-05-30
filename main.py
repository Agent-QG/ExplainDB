from agent.agent_builder import build_agent
from agent.agent_runner import ask_question
import pandas as pd
import matplotlib.pyplot as plt
import ast
import numpy as np
import ast
import pandas as pd
import re


if __name__ == "__main__":
    search_result = "[(1, 'Luís', 'Gonçalves', 'luisg@embraer.com.br', 15, 8), (2, 'Leonie', 'Köhler', 'leonekohler@surfeu.de', 17, 7), (3, 'François', 'Tremblay', 'ftremblay@gmail.com', 21, 10), (4, 'Bjørn', 'Hansen', 'bjorn.hansen@yahoo.no', 18, 8), (5, 'František', 'Wichterlová', 'frantisekw@jetbrains.com', 14, 8), (6, 'Helena', 'Holý', 'hholy@gmail.com', 13, 9), (7, 'Astrid', 'Gruber', 'astrid.gruber@apple.at', 11, 9), (8, 'Daan', 'Peeters', 'daan_peeters@apple.be', 13, 4), (9, 'Kara', 'Nielsen', 'kara.nielsen@jubii.dk', 15, 5), (10, 'Eduardo', 'Martins', 'eduardo@woodstock.com.br', 14, 7), (11, 'Alexandre', 'Rocha', 'alero@uol.com.br', 16, 6), (12, 'Roberto', 'Almeida', 'roberto.almeida@riotur.gov.br', 16, 5), (13, 'Fernanda', 'Ramos', 'fernadaramos4@uol.com.br', 20, 7), (14, 'Mark', 'Philips', 'mphilips12@shaw.ca', 19, 10), (15, 'Jennifer', 'Peterson', 'jenniferp@rogers.ca', 17, 8), (16, 'Frank', 'Harris', 'fharris@google.com', 9, 7), (17, 'Jack', 'Smith', 'jacksmith@microsoft.com', 13, 10), (18, 'Michelle', 'Brooks', 'michelleb@aol.com', 15, 6), (19, 'Tim', 'Goyer', 'tgoyer@apple.com', 16, 9), (20, 'Dan', 'Miller', 'dmiller@comcast.com', 17, 7), (21, 'Kathy', 'Chase', 'kachase@hotmail.com', 16, 9), (22, 'Heather', 'Leacock', 'hleacock@gmail.com', 16, 8), (23, 'John', 'Gordon', 'johngordon22@yahoo.com', 19, 9), (24, 'Frank', 'Ralston', 'fralston@gmail.com', 19, 10), (25, 'Victor', 'Stevens', 'vstevens@yahoo.com', 15, 8)]"

    agent = build_agent()
    question = "Which countries have the highest total revenue?"
    # - trace_log: the reasoning and SQL generation process,
    # - final_answer: the natural language answer,
    # - search_result: the SQL execution result.
    trace_log, final_answer, search_result = ask_question(agent, question)

    def extract_dataframe_from_trace(trace_log, search_result):
        """
        Extract SQL query column names from the trace_log and automatically build a DataFrame from the search_result.
        """

        # Step 1: Extract the SQL query (the last AI/Tool message that contains SELECT)
        sql_code = None
        for msg in reversed(trace_log):
            if msg.get("type") in ["ToolMessage", "AIMessage"] and "SELECT" in msg.get("content", "").upper():
                sql_code = msg["content"]
                break

        if not sql_code:
            raise ValueError("No SQL found in trace_log.")

        # Step 2: Parse the fields after SELECT in the SQL query
        pattern = r"SELECT\s+(.*?)\s+FROM"
        match = re.search(pattern, sql_code, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Could not parse SELECT columns.")

        raw_fields = match.group(1)

        # Handle field aliases using AS, e.g., COUNT(DISTINCT ar.ArtistId) AS artist_count
        field_names = []
        for field in raw_fields.split(","):
            field = field.strip()
            if " AS " in field.upper():
                alias = field.split(" AS ")[-1]
                field_names.append(alias.strip().strip("`\""))
            else:
                parts = field.split(".")
                name = parts[-1].strip("`\"")
                field_names.append(name)

        # Step 3: Parse search_result (if it's a string)
        if isinstance(search_result, str):
            try:
                search_result = ast.literal_eval(search_result)
            except Exception as e:
                print("Failed to parse search_result:", e)
                return None

        # Step 4: Construct the DataFrame
        try:
            df = pd.DataFrame(search_result, columns=field_names)
            json_str = df.to_json(orient='records', force_ascii=False, indent=2)

            # Write to json file
            with open("json_output/output.json", "w", encoding="utf-8") as f:
                f.write(json_str)
        except Exception as e:
            print("Failed to construct DataFrame:", e)
            return None

        return df

    print(extract_dataframe_from_trace(trace_log, search_result))


