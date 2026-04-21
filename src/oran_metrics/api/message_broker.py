"""Message Broker - Simulates RIC Message Router (RMR).

In real O-RAN SC, RMR handles message routing between xApps.
This is a simplified version to understand the pub/sub pattern.
"""
import time
import json
import random
import threading
from collections import defaultdict


class RICMessageRouter:
    """Simulated RIC Message Router (RMR)."""

    # Message type IDs (similar to real RMR message types)
    E2_INDICATION = 12050
    A1_POLICY_REQ = 20010
    LATENCY_ALERT = 30001
    PRB_ALERT = 30002

    def __init__(self):
        self.subscribers = defaultdict(list)
        self.message_log = []
        self.running = False

    def subscribe(self, msg_type, callback, subscriber_name="unknown"):
        """Subscribe to a message type."""
        self.subscribers[msg_type].append({
            "callback": callback,
            "name": subscriber_name,
        })
        print(f"  [RMR] {subscriber_name} subscribed to msg_type {msg_type}")

    def publish(self, msg_type, payload):
        """Publish a message to all subscribers of that type."""
        message = {
            "msg_type": msg_type,
            "payload": payload,
            "timestamp": time.time(),
        }
        self.message_log.append(message)

        delivered = 0
        for sub in self.subscribers.get(msg_type, []):
            sub["callback"](payload)
            delivered += 1

        return delivered

    def get_stats(self):
        """Get broker statistics."""
        return {
            "total_messages": len(self.message_log),
            "subscribers": {
                msg_type: len(subs)
                for msg_type, subs in self.subscribers.items()
            },
        }


# --- xApp implementations ---

class VRUSafetyXApp:
    """VRU Safety xApp - subscribes to E2 metrics, publishes alerts."""

    def __init__(self, rmr):
        self.rmr = rmr
        self.alerts = []
        rmr.subscribe(
            RICMessageRouter.E2_INDICATION,
            self.on_e2_indication,
            "VRU-Safety-xApp",
        )

    def on_e2_indication(self, payload):
        """Process incoming E2 metric report."""
        gnb = payload["gnb_id"]
        tp = payload["throughput_mbps"]
        latency = payload.get("latency_ms", 0)

        # Check if latency exceeds Near-RT budget
        if latency > 8:
            alert = {
                "gnb_id": gnb,
                "alert": "HIGH_LATENCY",
                "latency_ms": latency,
                "action": "redirect VRU traffic",
            }
            self.alerts.append(alert)
            self.rmr.publish(RICMessageRouter.LATENCY_ALERT, alert)
            print(f"    [VRU-xApp] ALERT: {gnb} latency {latency}ms > 8ms!")


class TrafficSteeringXApp:
    """Traffic Steering xApp - subscribes to PRB alerts."""

    def __init__(self, rmr):
        self.rmr = rmr
        self.actions = []
        rmr.subscribe(
            RICMessageRouter.PRB_ALERT,
            self.on_prb_alert,
            "Traffic-Steering-xApp",
        )
        rmr.subscribe(
            RICMessageRouter.LATENCY_ALERT,
            self.on_latency_alert,
            "Traffic-Steering-xApp",
        )

    def on_prb_alert(self, payload):
        """Handle PRB congestion alert."""
        action = {
            "type": "handover",
            "from_gnb": payload["gnb_id"],
            "reason": f"PRB utilization {payload['prb_pct']}% > 85%",
        }
        self.actions.append(action)
        print(f"    [TS-xApp] ACTION: Handover from {payload['gnb_id']} (PRB={payload['prb_pct']}%)")

    def on_latency_alert(self, payload):
        """Handle latency alert from VRU xApp."""
        action = {
            "type": "reroute",
            "gnb": payload["gnb_id"],
            "reason": payload["alert"],
        }
        self.actions.append(action)
        print(f"    [TS-xApp] ACTION: Reroute traffic for {payload['gnb_id']}")


class PRBMonitorXApp:
    """PRB Monitor xApp - watches utilization and publishes alerts."""

    def __init__(self, rmr):
        self.rmr = rmr
        rmr.subscribe(
            RICMessageRouter.E2_INDICATION,
            self.on_e2_indication,
            "PRB-Monitor-xApp",
        )

    def on_e2_indication(self, payload):
        """Check PRB utilization."""
        prb_pct = payload.get("prb_utilization_pct", 0)
        if prb_pct > 85:
            alert = {
                "gnb_id": payload["gnb_id"],
                "prb_pct": prb_pct,
                "alert": "HIGH_PRB_UTILIZATION",
            }
            self.rmr.publish(RICMessageRouter.PRB_ALERT, alert)
            print(f"    [PRB-xApp] ALERT: {payload['gnb_id']} PRB={prb_pct}% > 85%!")


if __name__ == "__main__":
    print("=== RIC Message Router (RMR) Demo ===\n")

    # 1. Create the message router
    rmr = RICMessageRouter()
    print("[1] Initializing xApps...\n")

    # 2. Create xApps (they auto-subscribe)
    vru_xapp = VRUSafetyXApp(rmr)
    ts_xapp = TrafficSteeringXApp(rmr)
    prb_xapp = PRBMonitorXApp(rmr)

    print(f"\n[2] Simulating gNB metric reports...\n")

    # 3. Simulate E2 INDICATION messages from gNBs
    reports = [
        {"gnb_id": "gNB-1", "throughput_mbps": 50.0, "latency_ms": 6.5,
         "prb_utilization_pct": 72.0},
        {"gnb_id": "gNB-2", "throughput_mbps": 38.0, "latency_ms": 9.2,
         "prb_utilization_pct": 91.0},
        {"gnb_id": "gNB-3", "throughput_mbps": 45.0, "latency_ms": 5.1,
         "prb_utilization_pct": 88.0},
        {"gnb_id": "gNB-1", "throughput_mbps": 42.0, "latency_ms": 11.0,
         "prb_utilization_pct": 95.0},
    ]

    for i, report in enumerate(reports):
        print(f"  --- E2 Report {i+1}: {report['gnb_id']} ---")
        rmr.publish(RICMessageRouter.E2_INDICATION, report)
        print()

    # 4. Summary
    print("[3] Summary\n")
    stats = rmr.get_stats()
    print(f"  Total messages routed: {stats['total_messages']}")
    print(f"  VRU alerts: {len(vru_xapp.alerts)}")
    print(f"  TS actions: {len(ts_xapp.actions)}")
    print()
    print("=== Demo complete ===")
