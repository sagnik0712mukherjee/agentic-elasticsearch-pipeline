from elasticsearch import Elasticsearch, helpers
from config import config
from src.observability.slack import slack

def s8_push_es(state):
    slack("Starting S8: Push to ES")
    es = Elasticsearch(
        hosts=[config.ELASTICSEARCH_URL],
        basic_auth=(config.ELASTICSEARCH_USER, config.ELASTICSEARCH_PASSWORD)
    )

    index_name = state["es_index"]
    df = state["final_df"]

    actions = [
        {
            "_index": index_name,
            "_id": row["item_id"],
            "_source": row
        }
        for row in df.to_dict(orient="records")
    ]

    helpers.bulk(es, actions)

    state["es_push_status"] = "SUCCESS"
    slack(f"✅ Successfully pushed {len(actions)} items to Elasticsearch index '{index_name}'.")
    return state
