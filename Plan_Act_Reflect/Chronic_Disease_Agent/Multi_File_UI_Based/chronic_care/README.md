# Chronic Care — LangGraph UI POC

Overview
- This folder contains a LangGraph-based UI proof-of-concept and a small Flask web UI that exercises the PLAN → ACT → REFLECT graph.
- Key files:
  - `langgraph_app.py`: Graph state and node implementations (PLAN, ACT, REFLECT).
  - `web_ui.py`: Small Flask app that runs the graph programmatically and renders results.
  - `run_graph_demo.py`: Helper/demo runner for the LangGraph graph.
  - `launch_langgraph_editor.py`: Exports `langgraph_project.json` for manual import into a LangGraph visual editor (auto-launch may not be available).

Requirements
- Python 3.11 (recommended) and a virtual environment.
- Install dependencies defined in `requirements.txt` from this folder:

```bash
cd "c:/Rajesh/R_D_Projects/AgenticAI/AgenticAI_DesignPatterns/Plan_Act_Reflect/Chronic_Disease_Agent/Multi_File_UI_Based/chronic_care"
python -m pip install -r requirements.txt
```

Run the Flask UI

```bash
python web_ui.py
# Open http://127.0.0.1:8501 in your browser
```

Notes on LangGraph visual editor
- The `launch_langgraph_editor.py` writes a `langgraph_project.json` file representing the graph. If your installed `langgraph` package does not provide a visual editor/CLI, import the JSON manually into the LangGraph editor (if you use a separate editor build).

Quick commands
- Export the project JSON for manual import:

```bash
python launch_langgraph_editor.py
```

- Run the programmatic graph demo (no UI):

```bash
python run_graph_demo.py
```

Developer notes
- `web_ui.py` builds a `CoachState` and calls the LangGraph graph programmatically. If you change `langgraph_app.py`'s state schema, update the UI accordingly.
