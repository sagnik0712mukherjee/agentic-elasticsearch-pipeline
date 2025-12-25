import pandas as pd
from observability.slack import slack

# In-memory cache for dynamically generated operations
DYNAMIC_OPS = {}

def safe_str_op(s, op):
    """Helper function for safe string operations (available to generated code)"""
    if s.dtype == "object" or pd.api.types.is_string_dtype(s):
        return op(s)
    return s

def execute_dynamic_op(op_name, df, target, op_context, generator_func):
    """
    Execute a dynamically generated operation.
    Check cache first, generate if needed.
    
    Args:
        op_name: Name of the operation
        df: pandas DataFrame for context/transformation
        target: The specific column name being calculated
        op_context: Specific rule context
        generator_func: Function to generate code if not cached
    
    Returns:
        Transformed pandas Series
    """
    # Check if operation is already cached
    if op_name in DYNAMIC_OPS:
        slack(f"♻️ Using cached operation: '{op_name}'")
        return DYNAMIC_OPS[op_name](df)
    
    # Generate new operation
    slack(f"🆕 Generating new operation: '{op_name}'")
    code = generator_func(op_name, df, target, op_context)
    
    # Execute the generated code in a controlled namespace
    namespace = {
        'pd': pd,
        'safe_str_op': safe_str_op
    }
    
    try:
        exec(code, namespace)
        
        # Extract the generated function
        if op_name in namespace:
            generated_func = namespace[op_name]
            
            # Cache it for future use
            DYNAMIC_OPS[op_name] = generated_func
            
            slack(f"✅ Successfully created and cached '{op_name}'")
            
            # Execute and return
            return generated_func(df)
        else:
            raise Exception(f"Generated code did not define function '{op_name}'")
            
    except Exception as e:
        slack(f"❌ Error executing generated operation '{op_name}': {str(e)}")
        raise Exception(f"Failed to execute dynamic operation '{op_name}': {str(e)}")
