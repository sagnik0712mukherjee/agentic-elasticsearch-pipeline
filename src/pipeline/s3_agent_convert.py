import json
from src.agents.profiler_agent import profile_raw
from src.agents.planner_agent import create_plan
from src.executor.apply_plan import apply_plan
from src.observability.slack import slack

def s3_agent_convert(state):
    slack("Starting S3: Agent Conversion")
    raw_df = state["raw_df"]
    es_schema = state["es_schema"]

    # Load business rules
    with open("src/data/rules/business_rules.json") as f:
        business_rules = json.load(f)

    # Sample first 100 rows
    sample_df = raw_df.head(100).to_dict(orient="records")

    # Agent 1: Profile
    profile_output = profile_raw(sample_df, es_schema)
    slack("Profiler Agent finished.")

    # Agent 2: Plan (with business rules)
    transformation_rules = business_rules.get("transformation_rules", [])
    plan_json = create_plan(profile_output, es_schema, transformation_rules)
    slack(f"Planner Agent finished. Plan: {plan_json}")
    plan = json.loads(plan_json)

    # Execute on FULL dataset
    final_df = apply_plan(raw_df, plan, transformation_rules)

    state["final_df"] = final_df
    state["mapping_plan"] = plan

    return state
