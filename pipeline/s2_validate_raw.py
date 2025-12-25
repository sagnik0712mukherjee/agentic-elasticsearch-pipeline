from observability.slack import slack
import config

def s2_validate_raw(state):
    slack("Starting S2: Validate Raw Data")
    df = state["raw_df"]

    if df.empty:
        raise Exception("Raw file is empty")

    # Use discovered primary key from state, fallback to config
    pk = state.get("discovered_primary_key") or config.FILE_RULES.get("primary_key")
    
    if pk and pk in df.columns:
        initial_count = len(df)
        duplicates = df[df.duplicated(subset=[pk], keep="first")]
        num_duplicates = len(duplicates)

        if num_duplicates > 0:
            alert_on_duplicates = config.FILE_RULES.get("alert_on_duplicates", True)
            if alert_on_duplicates:
                slack(f"⚠️ Found {num_duplicates} duplicates based on '{pk}'.")
            
            dedup_strategy = config.FILE_RULES.get("deduplication_strategy")
            if dedup_strategy == "keep_first":
                df = df.drop_duplicates(subset=[pk], keep="first")
                slack(f"Cleaned duplicates. Rows reduced from {initial_count} to {len(df)}.")
                state["raw_df"] = df

    state["raw_validation_passed"] = True
    return state
