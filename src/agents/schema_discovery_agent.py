from langchain_openai import ChatOpenAI
from config import config
from src.observability.slack import slack

llm = ChatOpenAI(model=config.OPENAI_MODEL)

def discover_primary_key(raw_df, hints):
    """
    Uses LLM to automatically discover the primary key column from the raw data.
    """
    slack("Schema Discovery Agent is analyzing columns...")
    
    columns = list(raw_df.columns)
    sample_data = raw_df.head(5).to_dict(orient='records')
    
    prompt = f"""
    You are a schema discovery agent.
    
    Analyze these columns and sample data to identify the PRIMARY KEY column.
    
    Columns: {columns}
    
    Sample Data (first 5 rows):
    {sample_data}
    
    Hints for primary key columns: {hints}
    
    The primary key should be:
    - Unique for each row
    - Not null
    - Typically contains words like: {', '.join(hints)}
    
    Return ONLY the column name, nothing else.
    """
    
    result = llm.invoke(prompt).content.strip()
    
    # Clean up the result (remove quotes, whitespace)
    primary_key = result.replace('"', '').replace("'", "").strip()
    
    slack(f"Discovered primary key: {primary_key}")
    
    return primary_key
