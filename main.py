from agent.agent_builder import build_agent
from agent.agent_runner import ask_question

if __name__ == "__main__":
    question = " Which customers increased their total spending by at least 50% 2011 compared to 2010?"
    agent = build_agent()
    ask_question(agent, question)
