"""Core O-RAN metric calculators."""


def throughput(data_bits, time_seconds):
    """Calculate throughput in Mbps."""
    if time_seconds <= 0:
        raise ValueError("Time must be positive")
    return (data_bits / time_seconds) / 1e6


def latency_budget(processing_ms, transport_ms, queuing_ms):
    """Calculate total E2E latency for xApp control loop."""
    return processing_ms + transport_ms + queuing_ms


def spectral_efficiency(throughput_mbps, bandwidth_mhz):
    """Calculate spectral efficiency in bps/Hz."""
    if bandwidth_mhz <= 0:
        raise ValueError("Bandwidth must be positive")
    return throughput_mbps / bandwidth_mhz


def prb_utilization(used_prbs, total_prbs):
    """Calculate PRB utilization percentage."""
    if total_prbs <= 0:
        raise ValueError("Total PRBs must be positive")
    return (used_prbs / total_prbs) * 100


def sinr_to_cqi(sinr_db):
    """Map SINR (dB) to CQI index (3GPP TS 38.214)."""
    thresholds = [
        (-6.7, 0), (-4.7, 1), (-2.3, 2), (0.2, 3),
        (2.4, 4), (4.6, 5), (6.6, 6), (8.1, 7),
        (10.3, 8), (11.7, 9), (14.1, 10), (16.3, 11),
        (18.7, 12), (21.0, 13), (22.7, 14)
    ]
    cqi = 15
    for threshold, index in reversed(thresholds):
        if sinr_db < threshold:
            cqi = index
    return cqi