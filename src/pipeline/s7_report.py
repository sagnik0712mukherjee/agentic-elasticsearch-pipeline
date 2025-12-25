from src.observability.slack import slack

def s7_report(state):
    slack("Starting S7: Report Generation")
    
    variance = state.get("variance_report", {})
    raw_passed = state.get("raw_validation_passed")
    final_passed = state.get("final_validation_passed")
    validation_results = state.get("validation_report", [])
    
    # Format validation details
    validation_details = ""
    if validation_results:
        validation_details = "\n📊 *Validation Details:*\n"
        for res in validation_results:
            icon = "✅" if res["passed"] else "❌"
            validation_details += f"{icon} {res['rule']}\n"
            if not res["passed"]:
                validation_details += f"   - Failures: {res['fail_count']}\n"
                if res["fail_sample"]:
                    validation_details += f"   - Samples: {', '.join(map(str, res['fail_sample']))}\n"

    report_msg = f"""
    📊 *Pipeline Report*
    ------------------------
    ✅ Raw Validation: {raw_passed}
    ✅ Final Validation: {final_passed}
       {validation_details}
    📉 *Delta Metrics*
    - Existing in ES: {variance.get('existing_in_es')}
    - Incoming Batch: {variance.get('total_incoming')}
    ------------------------
    🆕 New Items: {variance.get('new_items')}
    🔄 Updated Items: {variance.get('updated_items')}
    """
    
    slack(report_msg)
    state["report"] = report_msg
    return state
