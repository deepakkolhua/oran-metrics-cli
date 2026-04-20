"""Tests for O-RAN metric calculators."""
import sys
sys.path.insert(0, "src")

from oran_metrics.calculator import *


def test_throughput():
    assert throughput(50_000_000, 1) == 50.0

def test_latency():
    assert latency_budget(3, 2, 1.5) == 6.5

def test_spectral_efficiency():
    assert spectral_efficiency(50, 20) == 2.5

def test_prb():
    assert round(prb_utilization(45, 52), 1) == 86.5

def test_cqi_high():
    assert sinr_to_cqi(25) == 15

def test_cqi_low():
    assert sinr_to_cqi(-10) == 0


if __name__ == "__main__":
    tests = [f for f in dir() if f.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            eval(f"{t}()")
            print(f"  PASS: {t}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t} - {e}")
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed")