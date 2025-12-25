from pipeline.s1_read import read_raw_file
from graph.ingestion_graph import build_graph
import json

def main(index):
    state = {}

    state["raw_df"] = read_raw_file(f"data/raw_csvs/{index}.csv")
    state["es_index"] = index

    with open("data/schema/es_schema.json") as f:
        state["es_schema"] = json.load(f)

    graph = build_graph()
    graph.invoke(state)

if __name__ == "__main__":
    index = input("Enter index name: ")
    main(index)