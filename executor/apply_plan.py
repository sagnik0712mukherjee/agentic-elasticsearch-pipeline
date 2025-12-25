from executor.ops import OPS
from executor.dynamic_ops import execute_dynamic_op
from agents.generator_agents.operation_generator_agent import generate_operation_code

def pick_best_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return df[c]
    raise Exception("No valid source column found")

def apply_plan(df, plan, transformation_rules):
    out = df.copy()

    for target, rule in plan["mappings"].items():
        # 1. Initialize the target column with the best source column
        out[target] = pick_best_column(df, rule["from"])
        op_contexts = rule.get("op_contexts", {})
        
        for op in rule["ops"]:
            if op in OPS:
                # Update incrementally
                out[target] = OPS[op](out[target])
            else:
                # Dynamic operations get the whole DataFrame 'out'
                # Pass 'target' so it knows which column it's refining
                op_context = op_contexts.get(op, transformation_rules)
                out[target] = execute_dynamic_op(op, out, target, op_context, generate_operation_code)
        
    return out[list(plan["mappings"].keys())]
