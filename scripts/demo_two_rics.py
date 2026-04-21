"""Demo: Non-RT RIC and Near-RT RIC communicating via A1 interface."""
import requests

NEARRT = "http://localhost:8000"
NONRT = "http://localhost:8001"

def main():
    print("=== Two-RIC Communication Demo ===\n")

    print("[1] CU/DU sending E2 reports to Near-RT RIC...\n")
    gnbs = [
        {"gnb_id": "gNB-1", "data_bits": 50000000, "time_seconds": 1,
         "sinr_db": 15.5, "used_prbs": 45, "total_prbs": 52},
        {"gnb_id": "gNB-2", "data_bits": 25000000, "time_seconds": 1,
         "sinr_db": 5.0, "used_prbs": 48, "total_prbs": 52},
    ]
    for gnb in gnbs:
        r = requests.post(f"{NEARRT}/e2/metric-report", json=gnb)
        print(f"  {gnb['gnb_id']}: {r.json()}")
    print()

    print("[2] Non-RT RIC rApp analyzing gNBs...\n")
    for gnb_id in ["gNB-1", "gNB-2"]:
        r = requests.get(f"{NONRT}/rapp/analyze/{gnb_id}")
        data = r.json()
        print(f"  {gnb_id}:")
        print(f"    Metrics: TP={data['current_metrics']['throughput_mbps']}Mbps CQI={data['current_metrics']['cqi']}")
        print(f"    Risk: {data['risk_level']}")
        for rec in data.get("recommendations", []):
            print(f"    -> {rec}")
    print()

    print("[3] Non-RT RIC sending A1 policy...\n")
    r = requests.post(f"{NONRT}/rapp/create-policy", json={
        "policy_type": "traffic-steering",
        "target_gnb": "gNB-2",
        "min_throughput_mbps": 30.0,
        "priority": "high",
    })
    print(f"  Policy: {r.json()}\n")

    print("[4] Health check...")
    nearrt_health = requests.get(f"{NEARRT}/health").json()
    nonrt_health = requests.get(f"{NONRT}/health").json()
    print(f"  Near-RT RIC: {nearrt_health}")
    print(f"  Non-RT RIC:  {nonrt_health}")
    print("\n=== Demo complete ===")

if __name__ == "__main__":
    main()
