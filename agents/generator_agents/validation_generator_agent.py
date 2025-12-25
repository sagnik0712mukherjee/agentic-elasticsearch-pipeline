from langchain_openai import ChatOpenAI
import config
from observability.slack import slack

llm = ChatOpenAI(model=config.OPENAI_MODEL)

def generate_validation_code(rule_text, sample_df):
    """
    Uses LLM to generate Python code for a validation rule.
    
    Args:
        rule_text: The validation rule in English (e.g., "item_price must be > 0")
        sample_df: Sample pandas DataFrame for context
    
    Returns:
        Python function code as string
    """
    slack(f"🔍 Validation Generator: Creating check for '{rule_text}'...")
    
    sample_data_str = sample_df.head(3).to_string()
    columns = list(sample_df.columns)
    
    prompt = f"""
    You are a Python code generator for pandas data validation.
    
    Generate a Python function to validate the following rule:
    "{rule_text}"
    
    Context:
    - You are given a pandas DataFrame 'df'.
    - Column names: {columns}
    - Sample data (first 3 rows):
    {sample_data_str}
    
    Requirements:
    1. Function name MUST be: 'validate_rule'
    2. Function MUST take a pandas DataFrame 'df' as input.
    3. Function MUST return a dictionary with:
       - 'passed': boolean (True if 0 failures)
       - 'fail_count': number of failing rows
       - 'fail_sample': a list of primary key values (from 'item_id') for failing rows (max 5)
       - 'message': a short summary of the result
    4. Handle missing columns gracefully by returning a failure with a clear message.
    5. DO NOT MODIFY THE DATAFRAME. Only evaluate it.
    
    Example output format:
    ```python
    def validate_rule(df):
        if 'item_price' not in df.columns:
            return {{'passed': False, 'fail_count': len(df), 'fail_sample': [], 'message': 'Column missing'}}
        
        failures = df[pd.to_numeric(df['item_price'], errors='coerce') <= 0]
        count = len(failures)
        sample = failures['item_id'].head(5).tolist() if 'item_id' in df.columns else []
        
        return {{
            'passed': count == 0,
            'fail_count': count,
            'fail_sample': sample,
            'message': f'Found {{count}} items with price <= 0' if count > 0 else 'All items have valid price'
        }}
    ```
    
    Return ONLY the function definition, no imports, no explanations.
    """
    
    response = llm.invoke(prompt).content.strip()
    
    if "```python" in response:
        response = response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        response = response.split("```")[1].split("```")[0].strip()
    
    slack(f"✅ Generated validation code for: {rule_text}\nCODE:\n{response}")
    
    return response
