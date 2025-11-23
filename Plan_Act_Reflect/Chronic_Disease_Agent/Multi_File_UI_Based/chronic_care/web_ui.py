import os
import sys
import json
import dataclasses
from typing import Any

from flask import Flask, redirect, render_template_string, request, url_for


# Ensure the Multi_File_Based `chronic_care` package is importable when running
# this script from the `Multi_File_UI_Based/chronic_care` folder. We add the
# sibling `Multi_File_Based` directory to `sys.path` if it exists.
here = os.path.dirname(__file__)
chronic_agent_root = os.path.dirname(os.path.dirname(here))
multi_based = os.path.join(chronic_agent_root, "Multi_File_Based")
if os.path.isdir(os.path.join(multi_based, "chronic_care")) and multi_based not in sys.path:
        sys.path.insert(0, multi_based)


from langgraph_app import graph, CoachState

try:
        from chronic_care.demo import build_fake_yesterday
except Exception:
        from demo import build_fake_yesterday  # type: ignore


app = Flask(__name__)


INDEX_HTML = """
<!doctype html>
<html>
    <head>
        <title>ChronicCare LangGraph UI</title>
        <meta charset="utf-8" />
        <style>
        body { font-family: Inter, Arial, sans-serif; margin: 24px; background: #fbfbfd; color: #111827; }
        .col { display: inline-block; vertical-align: top; width: 32%; margin-right: 1%; }
        pre { background: #ffffff; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(16,24,40,0.05); white-space: pre-wrap; }
        .state { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; font-size:13px; }
        .controls { margin-bottom: 12px; }
        button { padding: 8px 12px; border-radius: 8px; border: none; background: linear-gradient(90deg,#6366f1,#8b5cf6); color: #fff; cursor: pointer; box-shadow: 0 6px 18px rgba(99,102,241,0.15); transition: transform .12s ease, box-shadow .12s ease; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(99,102,241,0.18); }
        .card { background: #fff; border-radius: 10px; padding: 12px; margin-bottom: 8px; box-shadow: 0 6px 18px rgba(2,6,23,0.06); transition: transform .12s ease, box-shadow .12s ease; }
        .card:hover { transform: translateY(-4px); box-shadow: 0 18px 40px rgba(2,6,23,0.08); }
        .badge { display:inline-block; padding:4px 8px; border-radius:999px; font-weight:600; font-size:12px; color: #fff; }
        .badge.info { background:#10b981; }
        .badge.warning { background:#f59e0b; }
        .badge.critical { background:#ef4444; }
        .timestamp { color:#6b7280; font-size:12px; margin-left:8px; }
        #actions { display:flex; flex-direction:column; gap:8px; }
        </style>
    </head>
    <body>
        <h1>ChronicCare Coach — LangGraph UI</h1>

        <div class="controls">
            <form action="{{ url_for('run_plan') }}" method="post" style="display:inline-block;">
                <button type="submit">Run PLAN</button>
            </form>
            <form action="{{ url_for('run_act') }}" method="post" style="display:inline-block; margin-left:8px;">
                <button type="submit">Run ACT</button>
            </form>
            <form action="{{ url_for('run_reflect') }}" method="post" style="display:inline-block; margin-left:8px;">
                <button type="submit">Run REFLECT</button>
            </form>
            <form action="{{ url_for('run_demo') }}" method="post" style="display:inline-block; margin-left:8px;">
                <button type="submit">Run Full: PLAN → ACT → REFLECT</button>
            </form>
        </div>

        <div class="col">
            <h2>Input State</h2>
            {{ patient_state|safe }}
        </div>

        <div class="col">
            <h2>Plan</h2>
            {{ plan|safe }}
        </div>

        <div class="col">
        <h2>Actions</h2>
        <div id="actions">{{ actions_html|safe }}</div>
        </div>

        <div style="clear:both; margin-top: 16px;"></div>

        <div style="width:100%;">
        <h2>Reflection</h2>
        {{ reflection|safe }}
        </div>

        <div style="width:100%; margin-top:12px;">
        <h2>Updated Profile</h2>
        {{ updated_profile|safe }}
        </div>
    </body>
</html>
"""



def _to_primitive(obj: Any) -> Any:
    # Convert dataclasses and nested objects into plain Python types
    if dataclasses.is_dataclass(obj):
        return _to_primitive(dataclasses.asdict(obj))
    if isinstance(obj, dict):
        return {k: _to_primitive(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_primitive(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    try:
        return str(obj)
    except Exception:
        return repr(obj)


def serialize(obj: Any) -> str:
    """Return HTML-safe pretty representation of `obj` for the UI.

    - Dataclasses are converted to dicts and pretty-printed as JSON.
    - Non-serializable values fall back to `str()`.
    The result is a `<pre class='state'>` HTML block (safe to inject).
    """
    try:
        prim = _to_primitive(obj)
        pretty = json.dumps(prim, indent=2, ensure_ascii=False)
        html = f"<pre class='state'>{pretty}</pre>"
        return html
    except Exception:
        return "<pre class='state'>(unserializable)</pre>"


@app.route("/", methods=["GET"])
def index():
        # Show empty page with placeholder values
        empty = "(not run)"
        return render_template_string(
                INDEX_HTML,
                patient_state=empty,
                plan=empty,
                actions_html=empty,
                reflection=empty,
                updated_profile=empty,
        )


@app.route("/run", methods=["POST"])
def run_demo():
        yesterday_state = build_fake_yesterday()

        initial = CoachState(
                patient_state=yesterday_state,
                live_readings=yesterday_state.glucose_readings[-2:],
        )

        result = graph.invoke(initial)

        plan = result.get("plan")
        actions = result.get("actions", [])
        reflection = result.get("reflection")
        patient_state = result.get("patient_state")

        # Build HTML for actions with colored badges
        actions_html = []
        for a in actions:
                sev = getattr(a.severity, "value", str(a.severity))
                badge_class = "info" if sev == "info" else "warning" if sev == "warning" else "critical"
                action_html = (
                        f"<div class='card'><span class='badge {badge_class}'>" f"{sev.upper()}</span>"
                        f"<span class='timestamp'>{a.timestamp}</span>"
                        f"<div style='margin-top:8px'>{a.message}</div></div>"
                )
                actions_html.append(action_html)

        return render_template_string(
                INDEX_HTML,
                patient_state=serialize(yesterday_state),
                plan=serialize(plan),
                actions_html=''.join(actions_html),
                reflection=serialize(reflection),
                updated_profile=serialize(patient_state.profile),
        )


@app.route("/run_plan", methods=["POST"])
def run_plan():
    try:
        yesterday_state = build_fake_yesterday()
        from langgraph_app import plan_node

        state = CoachState(patient_state=yesterday_state, live_readings=yesterday_state.glucose_readings[-2:])
        plan_update = plan_node(state)
        plan = plan_update.get("plan")

        return render_template_string(
            INDEX_HTML,
            patient_state=serialize(yesterday_state),
            plan=serialize(plan),
            actions_html="(not run)",
            reflection="(not run)",
            updated_profile=serialize(yesterday_state.profile),
        )
    except Exception as e:
        return render_template_string(INDEX_HTML, patient_state="(error)", plan=f"Error: {e}", actions_html="(not run)", reflection="(not run)", updated_profile="(error)")


@app.route("/run_act", methods=["POST"])
def run_act():
    try:
        yesterday_state = build_fake_yesterday()
        from langgraph_app import plan_node, act_node

        # Build initial state and compute plan
        initial = CoachState(patient_state=yesterday_state, live_readings=yesterday_state.glucose_readings[-2:])
        plan = plan_node(initial).get("plan")

        # Now run ACT with plan included
        state = CoachState(patient_state=yesterday_state, live_readings=yesterday_state.glucose_readings[-2:], plan=plan)
        actions = act_node(state).get("actions", [])

        # Build HTML for actions with colored badges
        act_html = []
        for a in actions:
            sev = getattr(a.severity, "value", str(a.severity))
            badge_class = "info" if sev == "info" else "warning" if sev == "warning" else "critical"
            action_html = (
                f"<div class='card'><span class='badge {badge_class}'>" f"{sev.upper()}</span>"
                f"<span class='timestamp'>{a.timestamp}</span>"
                f"<div style='margin-top:8px'>{a.message}</div></div>"
            )
            act_html.append(action_html)

        return render_template_string(
            INDEX_HTML,
            patient_state=serialize(yesterday_state),
            plan=serialize(plan),
            actions_html=''.join(act_html),
            reflection="(not run)",
            updated_profile=serialize(yesterday_state.profile),
        )
    except Exception as e:
        return render_template_string(INDEX_HTML, patient_state="(error)", plan="(error)", actions_html=f"Error: {e}", reflection="(not run)", updated_profile="(error)")


@app.route("/run_reflect", methods=["POST"])
def run_reflect():
    try:
        yesterday_state = build_fake_yesterday()
        from langgraph_app import plan_node, reflect_node

        initial = CoachState(patient_state=yesterday_state, live_readings=yesterday_state.glucose_readings[-2:])
        plan = plan_node(initial).get("plan")

        reflect_out = reflect_node(CoachState(patient_state=yesterday_state, plan=plan))
        reflection = reflect_out.get("reflection")
        updated_state = reflect_out.get("patient_state")

        # reflection rendered as preformatted text; updated_profile shown below
        return render_template_string(
            INDEX_HTML,
            patient_state=serialize(yesterday_state),
            plan=serialize(plan),
            actions_html="(not run)",
            reflection=serialize(reflection),
            updated_profile=serialize(updated_state.profile),
        )
    except Exception as e:
        return render_template_string(INDEX_HTML, patient_state="(error)", plan="(error)", actions_html="(not run)", reflection=f"Error: {e}", updated_profile="(error)")


def run_server(host: str = "127.0.0.1", port: int = 8501) -> None:
        app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
        run_server()
