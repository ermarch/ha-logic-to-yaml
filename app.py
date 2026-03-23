import streamlit as st
import ast
import yaml
import re

def parse_duration(duration_str):
    """Converts '5m' to 00:05:00 or '1h' to 01:00:00 for HA."""
    match = re.match(r"(\d+)([smh])", str(duration_str))
    if not match:
        return duration_str
    
    value, unit = match.groups()
    if unit == 's': return f"00:00:{int(value):02d}"
    if unit == 'm': return f"00:{int(value):02d}:00"
    if unit == 'h': return f"{int(value):02d}:00:00"
    return duration_str

def parse_condition(node):
    # ... (previous logic for BoolOp and UnaryOp) ...

    # Handle Comparisons with optional duration: temp > 25
    if isinstance(node, ast.Compare):
        left = node.left.id if isinstance(node.left, ast.Name) else "unknown"
        ops = node.ops[0]
        threshold = node.comparators[0].value if isinstance(node.comparators[0], ast.Constant) else 0
        
        # Base condition
        condition = {
            "condition": "numeric_state",
            "entity_id": f"sensor.{left}"
        }
        
        if isinstance(ops, ast.Gt): condition["above"] = threshold
        elif isinstance(ops, ast.Lt): condition["below"] = threshold
        
        # Check for duration metadata (Advanced: using a 'for_' naming convention)
        # For simplicity in this UI, we look for 'temp_for_5m > 25' 
        # or we can check if the user wrapped it in a function: 'hold(temp > 25, "5m")'
        return condition

    # NEW: Handle a 'hold' function for durations: hold(temp > 25, "5m")
    elif isinstance(node, ast.Call) and node.func.id == "hold":
        base_cond = parse_condition(node.args[0])
        duration_raw = node.args[1].value if isinstance(node.args[1], ast.Constant) else "0"
        base_cond["for"] = parse_duration(duration_raw)
        return base_cond

    # ... (rest of the Name/State logic) ...

st.title("HA Logic to YAML")
user_input = st.text_input("Enter your logic (e.g., temp > 25 and is_home)", "is_home and temp > 25")

if st.button("Generate YAML"):
    try:
        tree = ast.parse(user_input, mode='eval')
        result = parse_logic(tree.body)
        st.code(yaml.dump(result, sort_keys=False), language="yaml")
    except Exception as e:
        st.error(f"Error: {e}")
