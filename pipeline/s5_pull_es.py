from elasticsearch import Elasticsearch, helpers
import config
from observability.slack import slack

def s5_pull_es(state):
    slack("Starting S5: Pull ES Data")
    es = Elasticsearch(
        hosts=[config.ELASTICSEARCH_URL],
        basic_auth=(config.ELASTICSEARCH_USER, config.ELASTICSEARCH_PASSWORD)
    )

    index_name = state["es_index"]
    
    # Check if index exists first to avoid 404 on scan
    if not es.indices.exists(index=index_name):
        existing_ids = set()
        count = 0
    else:
        # Scan for all _ids
        scan_gen = helpers.scan(
            es,
            index=index_name,
            query={"query": {"match_all": {}}},
            _source=False 
        )
        existing_ids = {doc["_id"] for doc in scan_gen}
        count = len(existing_ids)

    state["existing_es_data"] = {
        "item_count": count,
        "ids": existing_ids
    }
    
    slack(f"Found {count} existing items in ES.")

    return state
