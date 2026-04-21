"""Near-RT RIC API Server - Simulates E2 and A1 interfaces."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from oran_metrics.calculator import (
    throughput,
    latency_budget,
    prb_utilization,
    sinr_to_cqi,
)

app = FastAPI(
    title="Near-RT RIC API",
    description="Simulated O-RAN Near-RT RIC with E2 and A1 interfaces",
    version="0.1.0",
)

# --- Data Models (like E2 messages) ---

class E2MetricReport(BaseModel):
    """E2 INDICATION message from CU/DU to Near-RT RIC."""
    gnb_id: str
    data_bits: float
    time_seconds: float
    sinr_db: float
    used_prbs: int
    total_prbs: int

class A1Policy(BaseModel):
    """A1 Policy from Non-RT RIC to Near-RT RIC."""
    policy_id: str
    policy_type: str
    target_gnb: str
    min_throughput_mbps: Optional[float] = None
    max_latency_ms: Optional[float] = None
    priority: str = "medium"

class LatencyMeasurement(BaseModel):
    """Latency components for E2E budget."""
    processing_ms: float
    transport_ms: float
    queuing_ms: float

# --- In-memory storage (simulates RIC database) ---

ric_database = {
    "metrics": {},
    "policies": {},
    "xapp_results": {},
}

# --- E2 Interface (southbound: CU/DU → RIC) ---

@app.post("/e2/metric-report")
def receive_e2_metric(report: E2MetricReport):
    """Receive E2 INDICATION message from gNB."""
    tp = throughput(report.data_bits, report.time_seconds)
    cqi = sinr_to_cqi(report.sinr_db)
    prb = prb_utilization(report.used_prbs, report.total_prbs)

    result = {
        "gnb_id": report.gnb_id,
        "throughput_mbps": round(tp, 2),
        "cqi": cqi,
        "prb_utilization_pct": round(prb, 1),
        "status": "processed",
    }

    ric_database["metrics"][report.gnb_id] = result
    return result

@app.get("/e2/metrics/{gnb_id}")
def get_gnb_metrics(gnb_id: str):
    """Query stored metrics for a specific gNB."""
    if gnb_id not in ric_database["metrics"]:
        raise HTTPException(status_code=404, detail=f"No metrics for {gnb_id}")
    return ric_database["metrics"][gnb_id]

@app.get("/e2/metrics")
def get_all_metrics():
    """Query all stored gNB metrics."""
    return ric_database["metrics"]

# --- A1 Interface (northbound: Non-RT RIC → Near-RT RIC) ---

@app.post("/a1/policy")
def receive_a1_policy(policy: A1Policy):
    """Receive A1 Policy from Non-RT RIC (rApp)."""
    ric_database["policies"][policy.policy_id] = policy.model_dump()
    return {
        "policy_id": policy.policy_id,
        "status": "enforced",
        "message": f"Policy applied to {policy.target_gnb}",
    }

@app.get("/a1/policies")
def get_all_policies():
    """List all active A1 policies."""
    return ric_database["policies"]

# --- xApp Interface (internal RIC) ---

@app.post("/xapp/latency-check")
def xapp_latency_check(measurement: LatencyMeasurement):
    """xApp checks if latency is within Near-RT RIC budget."""
    total = latency_budget(
        measurement.processing_ms,
        measurement.transport_ms,
        measurement.queuing_ms,
    )
    within_budget = total < 10
    ric_type = "Near-RT RIC" if within_budget else "Non-RT RIC"

    return {
        "total_latency_ms": round(total, 2),
        "within_nearrt_budget": within_budget,
        "recommended_ric": ric_type,
    }

@app.get("/health")
def health_check():
    """RIC health check endpoint."""
    return {
        "status": "healthy",
        "metrics_count": len(ric_database["metrics"]),
        "policies_count": len(ric_database["policies"]),
    }
