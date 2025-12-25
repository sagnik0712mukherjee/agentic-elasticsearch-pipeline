import pandas as pd

def safe_str_op(s, op):
    # Apply string operation only if dtype is object/string
    if s.dtype == "object" or pd.api.types.is_string_dtype(s):
        return op(s)
    return s

def trim(s): return safe_str_op(s, lambda x: x.str.strip())
def lowercase(s): return safe_str_op(s, lambda x: x.str.lower())
def remove_currency(s): return safe_str_op(s, lambda x: x.str.replace(r"[₹,]", "", regex=True))
def to_float(s): return pd.to_numeric(s, errors='coerce')
def to_int(s): 
    # First ensure it's numeric, then round and convert to Int64
    numeric = pd.to_numeric(s, errors='coerce')
    return numeric.round().astype('Int64')
def to_title_case(s): return safe_str_op(s, lambda x: x.str.title())
def rupees_to_paise(s):
    # Convert rupees to paise (multiply by 100)
    numeric = pd.to_numeric(s, errors='coerce')
    return (numeric * 100).round().astype('Int64')
def validate_url(s): return s
def normalize_category(s): return safe_str_op(s, lambda x: x.str.lower().str.replace("&", "and"))

OPS = {
    "trim": trim,
    "lowercase": lowercase,
    "remove_currency": remove_currency,
    "to_float": to_float,
    "to_int": to_int,
    "to_title_case": to_title_case,
    "rupees_to_paise": rupees_to_paise,
    "validate_url": validate_url,
    "normalize_category": normalize_category
}
