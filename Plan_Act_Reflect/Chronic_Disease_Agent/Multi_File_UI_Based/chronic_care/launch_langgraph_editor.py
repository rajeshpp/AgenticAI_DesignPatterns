"""Launcher to open the LangGraph visual editor with this project's graph.

This script does two things:
- Exports a minimal JSON describing the `plan->act->reflect` graph so it can be
  imported into the LangGraph editor.
- Attempts to launch the LangGraph UI with `python -m langgraph.ui`.

If the editor cannot be launched programmatically, the script prints clear
instructions for importing the generated `langgraph_project.json` into the
LangGraph visual editor.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Dict, List


def ensure_package_on_path() -> None:
    # Add sibling Multi_File_Based implementation to sys.path so imports work
    here = os.path.dirname(__file__)
    chronic_agent_root = os.path.dirname(os.path.dirname(here))
    multi_based = os.path.join(chronic_agent_root, "Multi_File_Based")
    if os.path.isdir(os.path.join(multi_based, "chronic_care")) and multi_based not in sys.path:
        sys.path.insert(0, multi_based)


def build_minimal_project() -> Dict[str, object]:
    # We deliberately produce a minimal, editor-friendly spec that contains
    # nodes and edges and points each node at the Python function in
    # `langgraph_app.py` that implements it.
    nodes = [
        {"id": "plan", "label": "PLAN", "type": "python", "code": "langgraph_app.plan_node"},
        {"id": "act", "label": "ACT", "type": "python", "code": "langgraph_app.act_node"},
        {"id": "reflect", "label": "REFLECT", "type": "python", "code": "langgraph_app.reflect_node"},
    ]

    edges = [
        {"from": "START", "to": "plan"},
        {"from": "plan", "to": "act"},
        {"from": "act", "to": "reflect"},
        {"from": "reflect", "to": "END"},
    ]

    project = {
        "meta": {"name": "ChronicCare Coach (LangGraph export)"},
        "nodes": nodes,
        "edges": edges,
        "entry_point": "plan",
    }

    return project


def write_project_file(path: str, project: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)


def try_launch_langgraph_ui() -> bool:
    # Try a common way to launch the langgraph editor; this may vary by
    # installation. We try `python -m langgraph.ui` and fall back to telling
    # the user how to start it manually.
    try:
        subprocess.check_call([sys.executable, "-m", "langgraph.ui"])
        return True
    except Exception:
        return False


def main() -> None:
    ensure_package_on_path()

    project = build_minimal_project()
    out_path = os.path.join(os.getcwd(), "langgraph_project.json")
    write_project_file(out_path, project)

    print(f"Wrote LangGraph project to: {out_path}\n")

    launched = try_launch_langgraph_ui()
    if launched:
        print("Attempted to launch LangGraph UI (python -m langgraph.ui).\n")
        print("If the editor opened, use its import/open project feature to load the JSON file created above.")
    else:
        print("Could not launch the LangGraph UI automatically.\n")
        print("To open the graph visually: \n")
        print("1) Install LangGraph and run its editor (if not already installed):")
        print("   python -m pip install langgraph")
        print("2) Start the LangGraph editor (common command):")
        print("   python -m langgraph.ui")
        print("3) In the editor, use File → Import or Open and choose the generated file:")
        print(f"   {out_path}")


if __name__ == "__main__":
    main()
