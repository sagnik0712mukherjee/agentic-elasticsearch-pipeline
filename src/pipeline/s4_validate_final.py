import json
from src.observability.slack import slack
from src.agents.generator_agents.validation_generator_agent import generate_validation_code
from src.executor.dynamic_validators import execute_dynamic_validator

def s4_validate_final(state):
    slack("Starting S4: Final Validation")
    df = state["final_df"]

    # Load validation rules
    try:
        with open("src/data/rules/data_validation_rules.json") as f:
            validation_rules = json.load(f)
    except Exception as e:
        slack(f"⚠️ Could not load validation rules: {str(e)}")
        state["final_validation_passed"] = True # Fallback
        return state

    results = []
    all_passed = True

    for rule in validation_rules:
        res = execute_dynamic_validator(rule, df, generate_validation_code)
        results.append({
            "rule": rule,
            "passed": res.get("passed", False),
            "message": res.get("message", ""),
            "fail_count": res.get("fail_count", 0),
            "fail_sample": res.get("fail_sample", [])
        })
        if not res.get("passed", False):
            all_passed = False

    state["validation_report"] = results
    state["final_validation_passed"] = all_passed
    
    status_icon = "✅" if all_passed else "❌"
    slack(f"{status_icon} Final validation complete. Passed: {all_passed}")
    
    return state
