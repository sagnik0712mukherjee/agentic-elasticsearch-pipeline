import pandas as pd
from src.observability.slack import slack

# In-memory cache for dynamically generated validators
DYNAMIC_VALIDATORS = {}

def execute_dynamic_validator(rule_text, df, generator_func):
    """
    Execute a dynamically generated validation rule.
    """
    # Use rule hash or slug as key
    token = "".join(filter(str.isalnum, rule_text))[:50]
    
    if token in DYNAMIC_VALIDATORS:
        return DYNAMIC_VALIDATORS[token](df)
    
    # Generate new validator
    code = generator_func(rule_text, df)
    
    namespace = {
        'pd': pd,
        'slack': slack
    }
    
    try:
        exec(code, namespace)
        
        if 'validate_rule' in namespace:
            validator = namespace['validate_rule']
            DYNAMIC_VALIDATORS[token] = validator
            return validator(df)
        else:
            raise Exception("Generated code did not define 'validate_rule'")
            
    except Exception as e:
        slack(f"❌ Error executing validator for '{rule_text}': {str(e)}")
        return {
            'passed': False,
            'fail_count': 0,
            'fail_sample': [],
            'message': f"Validator Error: {str(e)}"
        }
