from fastapi import FastAPI, HTTPException
import json

from graph.discharge_graph import build_graph
from langfuse import observe

app = FastAPI()
graph = build_graph()

@observe(name="hospital_discharge_workflow")
@app.post("/discharge")
def run_discharge():
    try:
        patient = json.load(open("data/patient_sample.json"))
        return graph.invoke({"patient": patient})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
