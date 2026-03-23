# 📝 HA-Logic-Compiler

**Stop fighting with YAML indentation. Write logic like a programmer, deploy like a pro.**

`HA-Logic-Compiler` is a Python-based utility that translates standard programming syntax (if-elif-else, boolean operators, and numeric comparisons) into valid **Home Assistant** automation code.

## 🚀 Key Features

* **Logic to YAML**: Converts `and`, `or`, and `not` into nested Home Assistant condition blocks.
* **Action Support**: Translates Python `if-else` statements into HA `if-then` or `choose` actions.
* **Duration Handling**: Use the `hold()` function to easily add `for:` durations (e.g., `5m`, `10s`).
* **Numeric Parsing**: Automatically maps `>` and `<` to `numeric_state` with `above` and `below` keys.
* **Smart Prefixing**: Intelligently guesses entity types (e.g., `temp` becomes `sensor.temp`).

---

## 📖 Syntax Guide

| Feature | Python-Style Input | Generated HA YAML |
| :--- | :--- | :--- |
| **Boolean** | `is_home and is_night` | Nested `condition: and` |
| **Numeric** | `temperature > 25` | `condition: numeric_state` |
| **Duration** | `hold(temp > 25, "5m")` | Adds `for: 00:05:00` |
| **If-Then** | `if light_on: switch_off` | `if: ... then: ...` |
| **Complex** | `if hold(pantry_door, "2m"): notify` | `if: { cond: state, for: '00:02:00' } ...` |

---

## 🛠️ Example Usage

**Input Script:**
```python
if is_home and hold(temperature > 25, "10m"):
    fan_on
else:
    fan_off
```

---

**Generated YAML:**
```yaml
- if:
  - condition: and
    conditions:
      - condition: state
        entity_id: binary_sensor.is_home
        state: 'on'
      - condition: numeric_state
        entity_id: sensor.temperature
        above: 25
        for: '00:10:00'
  then:
    - service: fan.turn_on
  else:
    - service: fan.turn_off
```

## 🔗 Live converter

[HA Logic to YAML](https://ha-logic-compiler.streamlit.app/)

## 💻 Installation
**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/ha-logic-compiler.git](https://github.com/YOUR_USERNAME/ha-logic-compiler.git)
cd ha-logic-compiler
```

---

**2. Install requirements:**
```bash
pip install -r requirements.txt
```

---

**3. Run the Web UI:**
```bash
streamlit run app.py
```
