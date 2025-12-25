from langchain_openai import ChatOpenAI
from config import config
from src.observability.slack import slack

llm = ChatOpenAI(model=config.OPENAI_MODEL)

def generate_operation_code(op_name, sample_df, target, op_context):
    """
    Uses LLM to generate Python code for a missing operation.
    
    Args:
        op_name: Name of the operation (e.g., "to_uppercase")
        sample_df: Sample pandas DataFrame for context
        target: The name of the column being calculated/updated
        op_context: Specific business rule context
    
    Returns:
        Python function code as string
    """
    slack(f"🔧 Operation Generator: Creating code for '{op_name}'...")
    
    # Get sample data for context
    sample_data_str = sample_df.head(3).to_string()
    columns = list(sample_df.columns)
    
    prompt = f"""
    You are a Python code generator for pandas operations.
    
    Generate a Python function for the operation: "{op_name}"
    
    The problem statement is the following transformation rule:
    {op_context}
    
    Context:
    - You are given a pandas DataFrame 'df'.
    - You are specifically calculating the values for the column: "{target}"
    - Column names: {columns}
    - Sample data (first 3 rows):
    {sample_data_str}
    
    CRITICAL INSTRUCTIONS:
    1. If "{target}" already exists in 'df', it contains the results of a PREVIOUS operation in a transformation chain. USE IT as your primary base for further modification if the business rule applies to the current state of that column.
    2. DATA PRESERVATION: For all rows that DO NOT match the business rule conditions, you MUST return the existing value of the target column (if it exists) or the original base column. DO NOT return null/NaN for non-matching rows.
    
    Requirements:
    1. Function name MUST be exactly: {op_name}
    2. Function MUST take a pandas DataFrame 'df' as input
    3. Function MUST return a pandas Series (this series will be assigned back to the column "{target}")
    4. Handle errors gracefully (e.g., return df['{target}'] if it exists, otherwise return a safe default).
    5. For string operations, use helpers if needed or standard pandas .str accessor.
    
    Available helpers in namespace:
    - safe_str_op(s, op): Applies string operation only if dtype is object/string
    - pd: pandas library
    
    Example patterns:
    ```python
    def update_category(df):
        # Step 1: Start with the CURRENT state of the target column
        current = df['{target}']
        # Step 2: Define masks/conditions
        is_snack = current.astype(str).str.contains('Snack', case=False, na=False)
        # Step 3: Update ONLY matching rows, preserving others
        return current.mask(is_snack, 'SNACKS ON SALE!')
    ```
    
    Return ONLY the function definition, no imports, no explanations.
    """
    
    response = llm.invoke(prompt).content.strip()
    
    # Clean up the response (remove markdown code blocks if present)
    if "```python" in response:
        response = response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        response = response.split("```")[1].split("```")[0].strip()
    
    slack(f"✅ Generated code for '{op_name}'\nContext: {op_context}\nSample Data: {sample_data_str}\nCODE:\n{response}")
    
    return response
