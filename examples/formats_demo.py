"""Comparing data formats used in O-RAN."""
import json
import yaml

# The same data in different formats

gnb_data = {
    "gnb_id": "gNB-1",
    "metrics": {
        "throughput_mbps": 50.0,
        "sinr_db": 15.5,
        "cqi": 11,
        "prb_utilization": 86.5,
    },
    "slice_config": [
        {"slice_id": 1, "type": "eMBB", "priority": "high"},
        {"slice_id": 2, "type": "URLLC", "priority": "critical"},
    ],
}

# --- JSON ---
print("=== JSON ===")
json_str = json.dumps(gnb_data, indent=2)
print(json_str)
print(f"Size: {len(json_str)} bytes\n")

# Write to file
with open("examples/gnb_data.json", "w") as f:
    json.dump(gnb_data, f, indent=2)

# Read back
with open("examples/gnb_data.json") as f:
    loaded = json.load(f)
print(f"Read back: {loaded['gnb_id']}, TP={loaded['metrics']['throughput_mbps']}Mbps\n")

# --- YAML ---
print("=== YAML ===")
yaml_str = yaml.dump(gnb_data, default_flow_style=False)
print(yaml_str)
print(f"Size: {len(yaml_str)} bytes\n")

# Write to file
with open("examples/gnb_data.yaml", "w") as f:
    yaml.dump(gnb_data, f, default_flow_style=False)

# Read back
with open("examples/gnb_data.yaml") as f:
    loaded = yaml.safe_load(f)
print(f"Read back: {loaded['gnb_id']}, TP={loaded['metrics']['throughput_mbps']}Mbps\n")

# --- Comparison ---
print("=== When to use what ===")
print("JSON  → APIs, machine-to-machine (E2/A1 messages)")
print("YAML  → Config files, human-readable settings")
print("Protobuf → High-speed binary, gRPC (real E2AP uses ASN.1/protobuf)")
