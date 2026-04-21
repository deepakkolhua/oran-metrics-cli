"""xApp Client - Simulates an xApp communicating with Near-RT RIC."""
import requests
import time
import random

RIC_URL = "http://localhost:8000"


def send_e2_report(gnb_id, data_bits, sinr_db, used_prbs, total_prbs):
    """Send E2 INDICATION message to Near-RT RIC."""
    payload = {
        "gnb_id": gnb_id,
        "data_bits": data_bits,
        "time_seconds": 1,
        "sinr_db": sinr_db,
        "used_prbs": used_prbs,
        "total_prbs": total_prbs,
    }
    response = requests.post(f"{RIC_URL}/e2/metric-report", json=payload)
    return response.json()


def get_metrics(gnb_id=None):
    """Query metrics from RIC."""
    if gnb_id:
        response = requests.get(f"{RIC_URL}/e2/metrics/{gnb_id}")
    else:
        response = requests.get(f"{RIC_URL}/e2/metrics")
    return response.json()


def send_a1_policy(policy_id, policy_type, target_gnb, priority="medium"):
    """Send A1 Policy to Near-RT RIC."""
    payload = {
        "policy_id": policy_id,
        "policy_type": policy_type,
        "target_gnb": target_gnb,
        "priority": priority,
    }
    response = requests.post(f"{RIC_URL}/a1/policy", json=payload)
    return response.json()


def check_latency(proc_ms, transport_ms, queue_ms):
    """Ask xApp to check latency budget."""
    payload = {
        "processing_ms": proc_ms,
        "transport_ms": transport_ms,
        "queuing_ms": queue_ms,
    }
    response = requests.post(f"{RIC_URL}/xapp/latency-check", json=payload)
    return response.json()


def simulate_gnb_stream(gnb_id, num_reports=5, interval=1):
    """Simulate a gNB sending periodic metric reports."""
    print(f"=== Simulating {gnb_id} — {num_reports} reports ===\n")

    for i in range(num_reports):
        sinr = round(random.uniform(5, 25), 1)
        prbs = random.randint(20, 50)
        bits = random.randint(20_000_000, 100_000_000)

        result = send_e2_report(gnb_id, bits, sinr, prbs, 52)

        print(f"  Report {i+1}: "
              f"TP={result['throughput_mbps']}Mbps  "
              f"CQI={result['cqi']}  "
              f"PRB={result['prb_utilization_pct']}%")

        time.sleep(interval)

    print(f"\n=== {gnb_id} stream complete ===")


if __name__ == "__main__":
    print("--- xApp Client Demo ---\n")

    # 1. Send metric reports from 3 gNBs
    for gnb in ["gNB-1", "gNB-2", "gNB-3"]:
        result = send_e2_report(
            gnb_id=gnb,
            data_bits=random.randint(30_000_000, 80_000_000),
            sinr_db=round(random.uniform(5, 20), 1),
            used_prbs=random.randint(20, 50),
            total_prbs=52,
        )
        print(f"E2 Report from {gnb}: {result}")

    print("")

    # 2. Send an A1 policy
    policy = send_a1_policy(
        policy_id="vru-safety-001",
        policy_type="vru-prioritization",
        target_gnb="gNB-1",
        priority="high",
    )
    print(f"A1 Policy: {policy}")
    print("")

    # 3. Check latency
    latency = check_latency(3, 2, 1.5)
    print(f"Latency Check: {latency}")
    print("")

    # 4. Query all metrics
    all_metrics = get_metrics()
    print(f"All RIC Metrics: {len(all_metrics)} gNBs registered")
    for gnb_id, metrics in all_metrics.items():
        print(f"  {gnb_id}: TP={metrics['throughput_mbps']}Mbps CQI={metrics['cqi']}")
