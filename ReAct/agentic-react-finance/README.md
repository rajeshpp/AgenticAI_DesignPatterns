# AgenticAI ReAct Finance Agent

This is a small ReAct-style agent that demonstrates reasoning and acting cycles for a finance use case: analyzing portfolio volatility using historical stock data.

## Setup

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

$ python agent.py --portfolio examples/sample_portfolio.json --days 30 --react-trace
```