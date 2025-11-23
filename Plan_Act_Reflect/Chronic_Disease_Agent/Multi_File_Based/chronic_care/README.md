# Chronic Care (Multi-file POC)

Purpose
- This folder contains the multi-file implementation of the ChronicCare coach used in the demos and by the UI POC. It implements agents, models and an easy-to-run `demo.py`.

Run the demo (local)
- Create and activate a Python venv (recommended) and use Python 3.11 or compatible.

```bash
cd "c:/Rajesh/R_D_Projects/AgenticAI/AgenticAI_DesignPatterns/Plan_Act_Reflect/Chronic_Disease_Agent/Multi_File_Based/chronic_care"
# optional: python -m venv .venv && source .venv/Scripts/activate (Windows: .\.venv\Scripts\activate)
python demo.py
```

Notes
- The demo is self-contained and should run without external dependencies in many setups. If you see an import error (`ModuleNotFoundError`) when running from a different working directory, run the script from this folder (see above) or run it as a package.

Run as package
- From the `Multi_File_Based` folder you can also run as a module:

```bash
cd "c:/Rajesh/R_D_Projects/AgenticAI/AgenticAI_DesignPatterns/Plan_Act_Reflect/Chronic_Disease_Agent/Multi_File_Based"
python -m chronic_care.demo
```

Developer notes
- This package is used by the UI POC located in `Multi_File_UI_Based/chronic_care`. The UI scripts import code from this package; keep public APIs (models, orchestrator) stable or update the UI accordingly.
