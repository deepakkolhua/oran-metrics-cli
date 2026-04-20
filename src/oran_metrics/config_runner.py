"""Run all metrics from a YAML config file."""
import yaml
from oran_metrics.calculator import (
    throughput,
    latency_budget,
    spectral_efficiency,
    prb_utilization,
    sinr_to_cqi,
)


def run_from_config(config_path):
    """Load config and run all calculations."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    exp = config["experiment"]
    gnb = config["gnb"]
    meas = config["measurements"]
    lat = config["latency"]

    print(f"=== {exp['name']} ===")
    print(f"Date: {exp['timestamp']}")
    print(f"gNB:  {gnb['id']}")
    print("")

    tp = throughput(meas["data_bits"], meas["time_seconds"])
    print(f"Throughput:    {tp:.2f} Mbps")

    se = spectral_efficiency(tp, gnb["bandwidth_mhz"])
    print(f"Spectral Eff:  {se:.2f} bps/Hz")

    prb = prb_utilization(gnb["used_prbs"], gnb["total_prbs"])
    print(f"PRB Util:      {prb:.1f}%")

    cqi = sinr_to_cqi(meas["sinr_db"])
    print(f"SINR {meas['sinr_db']} dB -> CQI {cqi}")

    total_lat = latency_budget(lat["processing_ms"], lat["transport_ms"], lat["queuing_ms"])
    ric = "Near-RT RIC" if total_lat < 10 else "Non-RT RIC"
    print(f"E2E Latency:   {total_lat:.2f} ms ({ric} compatible)")

    print("")
    print("=== All metrics computed ===")
