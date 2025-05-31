from langchain_core.runnables import RunnableConfig

config = RunnableConfig(recursion_limit=50)

def ask_question(agent, question):
    trace_log = []
    final_answer = None
    search_result = None

    last_message = None
    second_last_message = None
    i = 1

    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
        config=config
    ):
        message = step["messages"][-1]
        trace_log.append({
            "type": type(message).__name__,
            "content": getattr(message, "content", ""),
            "name": getattr(message, "name", None),
            "tool_input": getattr(message, "tool_input", None),
            "tool_output": getattr(message, "tool_output", None),
        })

        second_last_message = last_message
        last_message = message
        i += 1

    final_answer = getattr(last_message, "content", None)
    search_result = getattr(second_last_message, "content", None)

    return trace_log, final_answer, search_result
