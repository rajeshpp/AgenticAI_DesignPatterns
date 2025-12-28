from fastapi import FastAPI, HTTPException
import json
from graph.discharge_graph import build_graph

app = FastAPI()
graph = build_graph()

@app.post("/discharge")
def run_discharge():
    try:
        patient = json.load(open("data/patient_sample.json"))
        state = {"patient": patient}
        return graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
