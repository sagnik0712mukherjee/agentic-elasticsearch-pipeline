from src.observability.slack import slack

def s6_compare(state):
    slack("Starting S6: Compare Data")
    final_df = state["final_df"]
    existing_ids = state["existing_es_data"]["ids"]
    
    new_items_count = 0
    updated_items_count = 0
    
    if "item_id" in final_df.columns:
        current_ids = set(final_df["item_id"].astype(str))
        
        new_items_count = len(current_ids - existing_ids)
        updated_items_count = len(current_ids.intersection(existing_ids))
    
    state["variance_report"] = {
        "total_incoming": len(final_df),
        "existing_in_es": len(existing_ids),
        "new_items": new_items_count,
        "updated_items": updated_items_count
    }
    
    slack(f"📊 Delta calculated: {new_items_count} new, {updated_items_count} updates out of {len(final_df)} total items.")

    return state
