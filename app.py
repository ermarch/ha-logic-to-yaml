import ast
import yaml
import re
import streamlit as st

with st.expander("📖 View Documentation / Instructions"):
    try:
        with open("README.md", "r") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.error("README.md not found in the repository.")

# --- CORE COMPILER LOGIC ---

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
    """Parses Python AST into Home Assistant Condition YAML."""
    # Handle AND / OR
    if isinstance(node, ast.BoolOp):
        op_map = {ast.And: "and", ast.Or: "or"}
        return {
            "condition": op_map[type(node.op)],
            "conditions": [parse_condition(val) for val in node.values]
        }
    
    # Handle NOT
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return {"condition": "not", "conditions": [parse_condition(node.operand)]}
    
    # Handle hold(condition, "5m")
    elif isinstance(node, ast.Call) and node.func.id == "hold":
        base_cond = parse_condition(node.args[0])
        duration_raw = node.args[1].value if isinstance(node.args[1], ast.Constant) else "0"
        base_cond["for"] = parse_duration(duration_raw)
        return base_cond

    # Handle Comparisons (temp > 25)
    elif isinstance(node, ast.Compare):
        left = node.left.id if isinstance(node.left, ast.Name) else "unknown"
        ops = node.ops[0]
        threshold = node.comparators[0].value if isinstance(node.comparators[0], ast.Constant) else 0
        
        if isinstance(ops, (ast.Gt, ast.GtE)):
            return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "above": threshold}
        elif isinstance(ops, (ast.Lt, ast.LtE)):
            return {"condition": "numeric_state", "entity_id": f"sensor.{left}", "below": threshold}
        elif isinstance(ops, ast.Eq):
            return {"condition": "state", "entity_id": f"sensor.{left}", "state": threshold}

    # Handle Simple Names (is_home)
    elif isinstance(node, ast.Name):
        prefix = "binary_sensor" if "_" in node.id else "input_boolean"
        return {"condition": "state", "entity_id": f"{prefix}.{node.id}", "state": "on"}

    # Handle time(before="20:00:00", after="08:00:00")
    elif isinstance(node, ast.Call) and node.func.id == "time":
        time_cond = {"condition": "time"}
        for keyword in node.keywords:
            if keyword.arg in ["before", "after"]:
                # Ensure the time is wrapped in quotes for HA YAML
                time_cond[keyword.arg] = str(keyword.value.value)
        return time_cond

    return {"condition": "template", "value_template": "Check logic syntax"}

def parse_action(node):
    """Parses Python AST into Home Assistant Action YAML (if-then-else)."""
    if isinstance(node, ast.If):
        condition = parse_condition(node.test)
        then_actions = [parse_action(a) for a in node.body]
        
        if node.orelse:
            # Handle elif as a 'choose' block
            if isinstance(node.orelse[0], ast.If):
                return {
                    "choose": [
                        {"conditions": [condition], "sequence": then_actions},
                        parse_action(node.orelse[0])
                    ]
                }
            else:
                # Handle standard else
                else_actions = [parse_action(a) for a in node.orelse]
                return {
                    "if": [condition],
                    "then": then_actions,
                    "else": else_actions
                }
        return {"if": [condition], "then": then_actions}

    # Handle Service Calls (e.g., light_on)
    elif isinstance(node, (ast.Expr, ast.Call)):
        val = node.value if isinstance(node, ast.Expr) else node
        name = val.func.id if isinstance(val, ast.Call) else val.id
        return {"service": name.replace("_", "."), "target": {"entity_id": "TODO"}}

    return {"action": "manual_check"}

# --- STREAMLIT UI ---

st.set_page_config(page_title="HA Logic Compiler", page_icon="🤖")
st.title("🤖 HA Logic to YAML")
st.markdown("Write Python-style logic and get Home Assistant YAML instantly.")

with st.sidebar:
    st.header("Syntax Tips")
    st.code("hold(temp > 25, '5m')")
    st.code("if is_home and is_night:\n  light_on")
    st.info("Check the README for more examples.")

# --- EXAMPLE GALLERY ---
st.subheader("🚀 Quick Start Examples")
cols = st.columns(3)

# Define the examples
examples = {
    "Basic If-Else": "if is_home:\n    light_on\nelse:\n    light_off",
    "Numeric + Hold": "if hold(temperature > 25, '10m'):\n    ac_on",
    "Complex Logic": "if (is_home or guest_mode) and is_night:\n    security_arm_home"
}

# Create buttons in columns
for i, (name, code) in enumerate(examples.items()):
    if cols[i % 3].button(name):
        st.session_state.user_code = code

# --- TEXT AREA ---
# We link the value to session_state so the buttons can change it
if 'user_code' not in st.session_state:
    st.session_state.user_code = "if is_home:\n    light_on"

user_code = st.text_area("Edit your logic:", height=200, key="user_code")

# --- COMPILER BUTTON ---
if st.button("Compile to YAML", type="primary"):
    try:
        tree = ast.parse(user_code)
        result = [parse_action(stmt) for stmt in tree.body]
        yaml_output = yaml.dump(result, sort_keys=False)
        
        st.subheader("Resulting YAML:")
        
        # 1. Display with built-in copy button
        st.code(yaml_output, language="yaml")
        
        # 2. Add a Download Button
        st.download_button(
            label="💾 Download automation.yaml",
            data=yaml_output,
            file_name="automation.yaml",
            mime="text/yaml",
        )
        
        st.success("Compilation successful! You can now paste this into your Home Assistant automations.yaml.")
        
    except Exception as e:
        st.error(f"Syntax Error: {e}")
        st.info("Check your indentation or function brackets.")
