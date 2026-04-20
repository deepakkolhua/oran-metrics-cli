"""Command-line interface for O-RAN metrics."""
import argparse
from oran_metrics.calculator import throughput, latency_budget, sinr_to_cqi


def main():
    parser = argparse.ArgumentParser(description="O-RAN Metric Calculator")
    sub = parser.add_subparsers(dest="command")

    tp = sub.add_parser("throughput")
    tp.add_argument("--bits", type=float, required=True)
    tp.add_argument("--time", type=float, required=True)

    lat = sub.add_parser("latency")
    lat.add_argument("--proc", type=float, required=True)
    lat.add_argument("--transport", type=float, required=True)
    lat.add_argument("--queue", type=float, required=True)

    cqi = sub.add_parser("cqi")
    cqi.add_argument("--sinr", type=float, required=True)

    args = parser.parse_args()

    if args.command == "throughput":
        result = throughput(args.bits, args.time)
        print(f"Throughput: {result:.2f} Mbps")
    elif args.command == "latency":
        result = latency_budget(args.proc, args.transport, args.queue)
        ric = "Near-RT RIC" if result < 10 else "Non-RT RIC"
        print(f"E2E Latency: {result:.2f} ms ({ric} compatible)")
    elif args.command == "cqi":
        result = sinr_to_cqi(args.sinr)
        print(f"SINR {args.sinr} dB -> CQI {result}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
