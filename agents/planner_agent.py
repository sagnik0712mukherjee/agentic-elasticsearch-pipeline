from langchain_openai import ChatOpenAI
import config
from observability.slack import slack

llm = ChatOpenAI(model=config.OPENAI_MODEL)

def create_plan(profile_output, es_schema, transformation_rules=None):
    slack("Planner Agent is thinking...")
    
    # Format transformation rules for the prompt
    rules_text = ""
    if transformation_rules:
        rules_text = "\n\nBUSINESS TRANSFORMATION RULES (MUST APPLY):\n"
        for i, rule in enumerate(transformation_rules, 1):
            rules_text += f"{i}. {rule}\n"
    
    prompt = f"""
    You are a schema mapping planner.

    Based on this profile:
    {profile_output}

    Return a strict JSON mapping plan compatible with the execution engine.
    The format MUST be:
    {{
      "mappings": {{
        "target_es_field": {{
          "from": ["source_col_candidate_1", "source_col_candidate_2"],
          "ops": ["trim", "lowercase", "to_custom_op"],
          "op_contexts": {{
            "to_custom_op": "The EXACT business rule text from the list provided below that this operation implements."
          }}
        }}
      }}
    }}

    CRITICAL RULES:
    1. The keys in "mappings" MUST exist in the ES Schema provided in the profile. 
    2. Do NOT invent new fields. If a source column does not match any ES Schema field, IGNORE it.
    3. You can suggest ANY operation name that describes the transformation needed.
    4. Operation names MUST be simple Python function names (lowercase, underscores only, NO colons or special chars).
    5. Common ops: trim, lowercase, remove_currency, to_float, to_int, to_title_case, rupees_to_paise, validate_url, normalize_category.
    6. For business rules, suggest descriptive operation names (e.g., "to_uppercase", "remove_special_chars", "round_to_nearest_10").
    7. If an operation doesn't exist, the system will generate it automatically.
    8. Keep operations simple and focused - one transformation per operation.
    9. Remember that based on the rules provided, decide operations / functions. Add an operation if, and only if, it is absolutely necessary. Don't create random / unnecesary operations!

    Rules:
    {rules_text}

    Here is Final ES Schema:

    {es_schema}

    Return JSON only.
    """
    return llm.invoke(prompt).content
