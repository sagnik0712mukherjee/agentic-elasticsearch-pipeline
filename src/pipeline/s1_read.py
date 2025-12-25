import pandas as pd
import json
from src.observability.slack import slack
from src.agents.schema_discovery_agent import discover_primary_key

def read_raw_file(file_path):
    df = pd.read_csv(file_path)
    return df

def s1_read(state):
    slack("Starting S1: Read Data (Pass-through)")
    
    # Load business rules
    with open("src/data/rules/business_rules.json") as f:
        business_rules = json.load(f)
    
    # Discover primary key if auto-detection is enabled
    raw_df = state["raw_df"]
    hints = business_rules["data_source"]["hints_for_primary_key"]
    primary_key = discover_primary_key(raw_df, hints)
    state["discovered_primary_key"] = primary_key
    slack(f"Auto-detected primary key: {primary_key}")
    
    return state