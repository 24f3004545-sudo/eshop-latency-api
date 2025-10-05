from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import json
import os

# Load telemetry data
telemetry_file = os.path.join(os.path.dirname(__file__), "../telemetry.json")
with open(telemetry_file) as f:
    telemetry_data = json.load(f)

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# POST request body model
class LatencyRequest(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/api/latency")
def check_latency(req: LatencyRequest):
    result = {}
    for region in req.regions:
        records = [r for r in telemetry_data if r["region"] == region]
        if not records:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue
        latencies = [r["latency"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = sum(1 for l in latencies if l > req.threshold_ms)
        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(breaches)
        }
    return result
