# agent.py
"""
ReAct Agent runner for the AgenticAI ReAct Finance project.

Features added/updated:
 - Explicit ReAct trace output (OBSERVE -> REASON -> ACT -> REFLECT)
 - CLI flags:
     --portfolio <path>    : required portfolio JSON
     --days <int>          : lookback days for price data (default 30)
     --react-trace         : print structured ReAct trace (observation, plan, action_result, recommendation)
     --debug               : enable debug logging and print per-ticker summaries
 - Defensive printing for missing data and errors
"""

import argparse
import json
import time
import logging
from typing import Dict, Any, List

from tools.stock_tool import summarize_stock
from tools.portfolio_tool import analyze_portfolio
from tools.calculator_tool import recommend_action_by_vol

# Configure logger (used when --debug is passed)
logger = logging.getLogger("ReActAgent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
logger.addHandler(handler)


class ReActAgent:
    def __init__(self, days: int = 30):
        self.days = days
        self.memory: List[Dict[str, Any]] = []

    # ----------------
    # Observe
    # ----------------
    def observe(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        obs = {
            "type": "portfolio_load",
            "portfolio_name": portfolio.get("name"),
            "positions": portfolio.get("positions", []),
            "timestamp": time.time(),
        }
        self.memory.append({"phase": "observe", "data": obs, "timestamp": time.time()})
        return obs

    # ----------------
    # Reason
    # ----------------
    def reason(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        tickers = [p.get("ticker") for p in observation.get("positions", []) if p.get("ticker")]
        plan = {
            "intent": "summarize_tickers",
            "tickers": tickers,
            "days": self.days,
            "notes": "fetch per-ticker summaries then analyze portfolio",
        }
        self.memory.append({"phase": "reason", "data": plan, "timestamp": time.time()})
        return plan

    # ----------------
    # Act
    # ----------------
    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        summaries = []
        for t in plan.get("tickers", []):
            try:
                s = summarize_stock(t, plan.get("days", self.days))
            except Exception as e:
                s = {"ticker": t, "error": f"exception: {e}"}
            summaries.append(s)

        # Use the original loaded portfolio from memory (first observe entry)
        portfolio = next((m["data"]["portfolio_name"] for m in self.memory if m["phase"] == "observe"), None)
        # We still want position list for analysis
        positions = None
        for m in self.memory:
            if m["phase"] == "observe":
                positions = m["data"].get("positions", [])
                break

        p_analysis = analyze_portfolio(positions or [], summaries)

        result = {"summaries": summaries, "portfolio_analysis": p_analysis}
        self.memory.append({"phase": "act", "data": result, "timestamp": time.time()})
        return result

    # ----------------
    # Reflect
    # ----------------
    def reflect_and_recommend(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        p_analysis = action_result.get("portfolio_analysis", {})
        vol = p_analysis.get("weighted_annualized_volatility")
        if vol is None:
            rec = {"recommendation": "insufficient data", "volatility": None}
        else:
            rec = {"recommendation": recommend_action_by_vol(vol), "volatility": vol}
        self.memory.append({"phase": "reflect", "data": rec, "timestamp": time.time()})
        return rec

    # ----------------
    # Run (full loop)
    # ----------------
    def run(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        obs = self.observe(portfolio)
        plan = self.reason(obs)
        action_result = self.act(plan)
        recommendation = self.reflect_and_recommend(action_result)

        return {
            "observation": obs,
            "plan": plan,
            "action_result": action_result,
            "recommendation": recommendation,
            "memory": self.memory,
        }


# Utility: safe pretty-print JSON
def pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return str(obj)


def load_portfolio(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Run the AgenticAI ReAct Finance Agent")
    parser.add_argument("--portfolio", required=True, help="Path to portfolio JSON file")
    parser.add_argument("--days", type=int, default=30, help="Lookback days for historical data")
    parser.add_argument("--react-trace", action="store_true", help="Print the ReAct trace (observe->reason->act->reflect)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging and extra prints")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    portfolio = load_portfolio(args.portfolio)
    agent = ReActAgent(days=args.days)

    result = agent.run(portfolio)

    # Pretty console summary (existing behavior)
    print("\n=== Portfolio Analysis Summary ===\n")
    pa = result["action_result"].get("portfolio_analysis", {})
    if pa.get("error"):
        print("Error:", pa["error"])
        if "missing_tickers" in pa:
            print("Missing tickers:", pa["missing_tickers"])
    else:
        total_value = pa.get("total_value")
        if total_value is not None:
            print(f"Total value (approx): ${total_value:.2f}")
        wav = pa.get("weighted_annualized_volatility")
        if wav is not None:
            print(f"Weighted annualized volatility: {wav:.4f}")
        print("\nExposures:")
        for e in pa.get("exposures", []):
            wt = e.get("weight", 0.0) * 100
            print(f" - {e.get('ticker')}: {wt:.2f}%")

    print("\nRecommendation:")
    rec = result.get("recommendation", {})
    print(rec.get("recommendation"))

    # If debug, print per-ticker summaries for inspection
    if args.debug:
        print("\n--- Per-ticker summaries ---\n")
        print(pretty(result["action_result"].get("summaries", [])))

    # ReAct trace: structured printout of phases
    if args.react_trace:
        print("\n=== ReAct Trace ===\n")

        print("🟦 OBSERVE:")
        print(pretty(result["observation"]))

        print("\n🟩 REASON:")
        print(pretty(result["plan"]))

        print("\n🟨 ACT (Tool Outputs):")
        print(pretty(result["action_result"]))

        print("\n🟪 REFLECT:")
        print(pretty(result["recommendation"]))

        # Optional: show the memory timeline (structured)
        print("\n--- Memory Timeline (phases recorded) ---")
        for m in result.get("memory", []):
            phase = m.get("phase")
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m.get("timestamp", 0)))
            print(f"{ts}  {phase.upper()}: {json.dumps(m.get('data'), default=str)}")

    # exit
    return 0


if __name__ == "__main__":
    main()
