import streamlit as st
import ast
import yaml

import ast
import yaml

def parse_condition(node):
    # (Same logic as before for boolean/numeric parsing)
    if isinstance(node, ast.BoolOp):
        op_map = {ast.And: "and", ast.Or: "or"}
        return {"condition": op_map[type(node.op)], "conditions": [parse_condition(val) for val in node.values]}
    elif isinstance(node, ast.Compare):
        left = node.left.id if isinstance(node.left, ast.Name) else "unknown"
        ops = node.ops[0]
        threshold = node.comparators[0].value if isinstance(node.comparators[0], ast.Constant) else 0
        if isinstance(ops, ast.Gt): return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "above": threshold}
        if isinstance(ops, ast.Lt): return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "below": threshold}
    elif isinstance(node, ast.Name):
        return {"condition": "state", "entity_id": f"binary_sensor.{node.id}", "state": "on"}
    return {"condition": "template", "value_template": "TODO"}

def parse_action(node):
    # Handle 'if' statements (if-then-else)
    if isinstance(node, ast.If):
        condition = parse_condition(node.test)
        
        # 'then' block
        then_actions = [parse_action(a) for a in node.body]
        
        # 'else' or 'elif' block
        if node.orelse:
            # If the 'else' contains another 'if', it's a 'choose' or 'elif'
            if isinstance(node.orelse[0], ast.If):
                # This could be mapped to a HA 'choose' block
                return {
                    "choose": [
                        {"conditions": [condition], "sequence": then_actions},
                        # Recursively handle the next if (the elif)
                        parse_action(node.orelse[0])
                    ]
                }
            else:
                # Standard if-then-else
                else_actions = [parse_action(a) for a in node.orelse]
                return {
                    "if": [condition],
                    "then": then_actions,
                    "else": else_actions
                }
        
        return {"if": [condition], "then": then_actions}

    # Handle a simple function call (e.g., light.turn_on())
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        func_name = node.value.func.id if isinstance(node.value.func, ast.Name) else "service.call"
        return {"service": func_name.replace("_", "."), "target": {"entity_id": "TODO"}}

    return {"action": "manual_check_required"}

st.title("HA Logic to YAML")
user_input = st.text_input("Enter your logic (e.g., temp > 25 and is_home)", "is_home and temp > 25")

if st.button("Generate YAML"):
    try:
        tree = ast.parse(user_input, mode='eval')
        result = parse_logic(tree.body)
        st.code(yaml.dump(result, sort_keys=False), language="yaml")
    except Exception as e:
        st.error(f"Error: {e}")
