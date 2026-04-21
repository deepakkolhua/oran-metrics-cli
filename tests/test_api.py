"""Tests for Near-RT RIC API."""
from fastapi.testclient import TestClient
from oran_metrics.api.ric_server import app

client = TestClient(app)


# --- Health Check ---

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# --- E2 Interface Tests ---

def test_e2_metric_report():
    payload = {
        "gnb_id": "gNB-test",
        "data_bits": 50000000,
        "time_seconds": 1,
        "sinr_db": 15.5,
        "used_prbs": 45,
        "total_prbs": 52,
    }
    response = client.post("/e2/metric-report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gnb_id"] == "gNB-test"
    assert data["throughput_mbps"] == 50.0
    assert data["cqi"] == 11
    assert data["prb_utilization_pct"] == 86.5
    assert data["status"] == "processed"


def test_e2_get_metrics():
    # First send a report
    client.post("/e2/metric-report", json={
        "gnb_id": "gNB-query",
        "data_bits": 40000000,
        "time_seconds": 1,
        "sinr_db": 10.0,
        "used_prbs": 30,
        "total_prbs": 52,
    })
    # Then query it
    response = client.get("/e2/metrics/gNB-query")
    assert response.status_code == 200
    data = response.json()
    assert data["gnb_id"] == "gNB-query"
    assert data["throughput_mbps"] == 40.0


def test_e2_metrics_not_found():
    response = client.get("/e2/metrics/gNB-nonexistent")
    assert response.status_code == 404


# --- A1 Interface Tests ---

def test_a1_policy():
    payload = {
        "policy_id": "test-policy",
        "policy_type": "traffic-steering",
        "target_gnb": "gNB-1",
        "priority": "high",
    }
    response = client.post("/a1/policy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["policy_id"] == "test-policy"
    assert data["status"] == "enforced"


def test_a1_get_policies():
    response = client.get("/a1/policies")
    assert response.status_code == 200


# --- xApp Tests ---

def test_xapp_latency_within_budget():
    payload = {
        "processing_ms": 3,
        "transport_ms": 2,
        "queuing_ms": 1.5,
    }
    response = client.post("/xapp/latency-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_latency_ms"] == 6.5
    assert data["within_nearrt_budget"] == True
    assert data["recommended_ric"] == "Near-RT RIC"


def test_xapp_latency_exceeds_budget():
    payload = {
        "processing_ms": 5,
        "transport_ms": 4,
        "queuing_ms": 3,
    }
    response = client.post("/xapp/latency-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_latency_ms"] == 12.0
    assert data["within_nearrt_budget"] == False
    assert data["recommended_ric"] == "Non-RT RIC"
