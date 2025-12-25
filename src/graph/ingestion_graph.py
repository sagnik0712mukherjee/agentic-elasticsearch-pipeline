from langgraph.graph import StateGraph
from src.pipeline.s1_read import s1_read
from src.pipeline.s2_validate_raw import s2_validate_raw
from src.pipeline.s3_agent_convert import s3_agent_convert
from src.pipeline.s4_validate_final import s4_validate_final
from src.pipeline.s5_pull_es import s5_pull_es
from src.pipeline.s6_compare import s6_compare
from src.pipeline.s7_report import s7_report
from src.pipeline.s8_push_es import s8_push_es


def build_graph():
    g = StateGraph(dict)

    g.add_node("S1", s1_read)
    g.add_node("S2", s2_validate_raw)
    g.add_node("S3", s3_agent_convert)
    g.add_node("S4", s4_validate_final)
    g.add_node("S5", s5_pull_es)
    g.add_node("S6", s6_compare)
    g.add_node("S7", s7_report)
    g.add_node("S8", s8_push_es)

    g.set_entry_point("S1")
    g.add_edge("S1", "S2")
    g.add_edge("S2", "S3")
    g.add_edge("S3", "S4")
    g.add_edge("S4", "S5")
    g.add_edge("S5", "S6")
    g.add_edge("S6", "S7")
    g.add_edge("S7", "S8")

    return g.compile()
