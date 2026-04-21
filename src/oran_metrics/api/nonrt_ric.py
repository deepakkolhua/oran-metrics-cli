"""Non-RT RIC Server - Hosts rApps, sends A1 policies to Near-RT RIC."""
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(
    title="Non-RT RIC API",
    description="Hosts rApps and manages A1 policies",
    version="0.1.0",
)

NEARRT_RIC_URL = "http://localhost:8000"


class PolicyRequest(BaseModel):
    policy_type: str
    target_gnb: str
    min_throughput_mbps: float = None
    max_latency_ms: float = None
    priority: str = "medium"


# In-memory storage
policy_counter = {"count": 0}
rapp_insights = {}


@app.post("/rapp/create-policy")
def rapp_create_policy(req: PolicyRequest):
    """rApp analyzes and sends A1 policy to Near-RT RIC."""
    policy_counter["count"] += 1
    policy_id = f"policy-{policy_counter['count']:03d}"

    # Send to Near-RT RIC via A1
    a1_payload = {
        "policy_id": policy_id,
        "policy_type": req.policy_type,
        "target_gnb": req.target_gnb,
        "min_throughput_mbps": req.min_throughput_mbps,
        "max_latency_ms": req.max_latency_ms,
        "priority": req.priority,
    }

    try:
        response = requests.post(
            f"{NEARRT_RIC_URL}/a1/policy", json=a1_payload
        )
        nearrt_response = response.json()
    except requests.ConnectionError:
        return {"error": "Near-RT RIC not reachable", "policy_id": policy_id}

    return {
        "policy_id": policy_id,
        "nearrt_ric_response": nearrt_response,
        "status": "policy_sent_via_a1",
    }


@app.get("/rapp/analyze/{gnb_id}")
def rapp_analyze_gnb(gnb_id: str):
    """rApp fetches metrics from Near-RT RIC and provides recommendations."""
    try:
        response = requests.get(f"{NEARRT_RIC_URL}/e2/metrics/{gnb_id}")
        if response.status_code == 404:
            return {"error": f"No data for {gnb_id}"}
        metrics = response.json()
    except requests.ConnectionError:
        return {"error": "Near-RT RIC not reachable"}

    # rApp intelligence: analyze and recommend
    recommendations = []
    if metrics["prb_utilization_pct"] > 85:
        recommendations.append("HIGH_LOAD: Consider traffic steering")
    if metrics["cqi"] < 7:
        recommendations.append("LOW_CQI: Consider beam management")
    if metrics["throughput_mbps"] < 30:
        recommendations.append("LOW_THROUGHPUT: Check interference")

    insight = {
        "gnb_id": gnb_id,
        "current_metrics": metrics,
        "recommendations": recommendations,
        "risk_level": "high" if len(recommendations) >= 2 else "low",
    }
    rapp_insights[gnb_id] = insight
    return insight


@app.get("/health")
def health():
    return {
        "service": "Non-RT RIC",
        "status": "healthy",
        "policies_created": policy_counter["count"],
    }
