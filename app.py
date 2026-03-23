import streamlit as st
import ast
import yaml

def parse_logic(node):
    # 1. Handle AND / OR
    if isinstance(node, ast.BoolOp):
        op_map = {ast.And: "and", ast.Or: "or"}
        return {
            "condition": op_map[type(node.op)],
            "conditions": [parse_logic(val) for val in node.values]
        }
    
    # 2. Handle NOT
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return {"condition": "not", "conditions": [parse_logic(node.operand)]}
    
    # 3. Handle Comparisons (e.g., temp > 25)
    elif isinstance(node, ast.Compare):
        left = node.left.id if isinstance(node.left, ast.Name) else "unknown"
        ops = node.ops[0]
        threshold = node.comparators[0].value if isinstance(node.comparators[0], ast.Constant) else 0
        
        # Map Python operators to HA numeric_state keys
        if isinstance(ops, ast.Gt):
            return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "above": threshold}
        elif isinstance(ops, ast.Lt):
            return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "below": threshold}
        elif isinstance(ops, ast.Eq):
            return {"condition": "state", "entity_id": f"sensor.{left}", "state": threshold}

    # 4. Handle Simple Boolean Names (e.g., is_home)
    elif isinstance(node, ast.Name):
        return {"condition": "state", "entity_id": f"binary_sensor.{node.id}", "state": "on"}
    
    return {"error": "Unsupported logic structure"}

# Test it out:
#logic_input = "is_home and temperature > 22"
#tree = ast.parse(logic_input, mode='eval')
#print(yaml.dump(parse_logic(tree.body), sort_keys=False))

st.title("HA Logic to YAML")
user_input = st.text_input("Enter your logic (e.g., temp > 25 and is_home)", "is_home and temp > 25")

if st.button("Generate YAML"):
    try:
        tree = ast.parse(user_input, mode='eval')
        result = parse_logic(tree.body)
        st.code(yaml.dump(result, sort_keys=False), language="yaml")
    except Exception as e:
        st.error(f"Error: {e}")
