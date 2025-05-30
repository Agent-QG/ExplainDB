def ask_question(agent, question):
    trace_log = []
    final_answer = None
    search_result = None

    last_message = None
    second_last_message = None

    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
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

    final_answer = getattr(last_message, "content", None)
    search_result = getattr(second_last_message, "content", None)

    print(final_answer)
    return trace_log, final_answer, search_result
