from langchain_openai import ChatOpenAI
import config
from observability.slack import slack

llm = ChatOpenAI(model=config.OPENAI_MODEL)

def profile_raw(sample_rows, es_schema):
    slack("Profiler Agent is thinking...")
    prompt = f"""
    You are a data profiling agent.

    ES Schema:
    {es_schema}

    Raw Sample Rows:
    {sample_rows}

    Infer possible column meanings.
    Return JSON only.
    """
    return llm.invoke(prompt).content
