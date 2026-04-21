"""Simulated E2 message using protobuf-like binary encoding.

Real O-RAN E2AP uses ASN.1, but protobuf is the closest
practical equivalent for understanding binary serialization.
"""
import struct
import json


class E2MetricBinary:
    """Binary-encoded E2 metric report.
    
    Format: [gnb_id(4 bytes)][throughput(8 bytes float)]
            [sinr(8 bytes float)][prbs_used(4 bytes int)]
            [prbs_total(4 bytes int)]
    Total: 28 bytes vs ~200 bytes for JSON
    """

    STRUCT_FORMAT = "!I d d I I"  # network byte order

    @staticmethod
    def encode(gnb_num, throughput, sinr, used_prbs, total_prbs):
        """Encode metrics to binary."""
        return struct.pack(
            E2MetricBinary.STRUCT_FORMAT,
            gnb_num, throughput, sinr, used_prbs, total_prbs,
        )

    @staticmethod
    def decode(binary_data):
        """Decode binary to metrics."""
        gnb_num, tp, sinr, used, total = struct.unpack(
            E2MetricBinary.STRUCT_FORMAT, binary_data
        )
        return {
            "gnb_id": f"gNB-{gnb_num}",
            "throughput_mbps": round(tp, 2),
            "sinr_db": round(sinr, 1),
            "used_prbs": used,
            "total_prbs": total,
        }


if __name__ == "__main__":
    # Encode
    binary = E2MetricBinary.encode(1, 50.0, 15.5, 45, 52)
    print(f"Binary: {binary.hex()}")
    print(f"Binary size: {len(binary)} bytes")

    # Compare with JSON
    json_data = json.dumps({
        "gnb_id": "gNB-1",
        "throughput_mbps": 50.0,
        "sinr_db": 15.5,
        "used_prbs": 45,
        "total_prbs": 52,
    })
    print(f"JSON size:   {len(json_data)} bytes")
    print(f"Compression: {len(binary)/len(json_data)*100:.0f}% of JSON size")
    print()

    # Decode
    decoded = E2MetricBinary.decode(binary)
    print(f"Decoded: {decoded}")
    print()

    # Speed test
    import time
    N = 100000

    start = time.time()
    for i in range(N):
        E2MetricBinary.encode(1, 50.0, 15.5, 45, 52)
    binary_time = time.time() - start

    start = time.time()
    for i in range(N):
        json.dumps({"gnb_id": "gNB-1", "throughput_mbps": 50.0,
                     "sinr_db": 15.5, "used_prbs": 45, "total_prbs": 52})
    json_time = time.time() - start

    print(f"=== Speed test ({N} encodings) ===")
    print(f"Binary: {binary_time:.3f}s")
    print(f"JSON:   {json_time:.3f}s")
    print(f"Binary is {json_time/binary_time:.1f}x faster")
