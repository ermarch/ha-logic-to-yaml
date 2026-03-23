📝 HA-Logic-Compiler

Turn Python-style logic into Home Assistant YAML automations instantly.

Are you tired of nesting and and or conditions in Home Assistant YAML? This utility allows you to write natural programming logic and converts it into valid, indented HA-compliant YAML code.
🚀 Features

    Boolean Mapping: Automatically converts and, or, and not into nested HA blocks.

    Numeric Comparisons: Recognizes > and < to generate numeric_state conditions.

    Smart Entity Tagging: Automatically prefixes sensors (e.g., temp becomes sensor.temp).

    Streamlit Web Interface: A clean UI to paste logic and copy YAML.

🛠️ How It Works

Input your logic in standard Python syntax:
Python

is_home and (temperature > 22 or guest_mode)

The compiler parses the Abstract Syntax Tree (AST) and generates:
YAML

condition: and
conditions:
  - condition: state
    entity_id: binary_sensor.is_home
    state: 'on'
  - condition: or
    conditions:
      - condition: numeric_state
        entity_id: sensor.temperature
        above: 22
      - condition: state
        entity_id: binary_sensor.guest_mode
        state: 'on'

💻 Installation & Local Usage

    Clone the repository:
    Bash

    git clone https://github.com/YOUR_USERNAME/ha-logic-compiler.git
    cd ha-logic-compiler

    Install dependencies:
    Bash

    pip install -r requirements.txt

    Run the Streamlit app:
    Bash

    streamlit run app.py

🌐 Deploying to the Web

This project is configured for Streamlit Community Cloud:

    Push this code to your GitHub repository.

    Visit share.streamlit.io.

    Connect your repository.

    Your compiler is now live at https://your-app-name.streamlit.app!

🗺️ Roadmap

    [ ] Support for for: duration (e.g., temp > 25 for 5m)

    [ ] Integration with Home Assistant API to fetch real entity IDs

    [ ] Support for choose: and if-then-else action blocks

    [ ] Export directly to automations.yaml

🤝 Contributing

Feel free to open an issue or submit a pull request if you have ideas for better logic mapping or support for more Home Assistant platforms!
