"""Tests for YAML config runner."""
import os
import yaml
from oran_metrics.config_runner import run_from_config


def test_config_file_exists():
    assert os.path.exists("examples/config.yaml")


def test_config_loads():
    with open("examples/config.yaml") as f:
        config = yaml.safe_load(f)
    assert "experiment" in config
    assert "gnb" in config
    assert "measurements" in config
    assert "latency" in config


def test_config_values():
    with open("examples/config.yaml") as f:
        config = yaml.safe_load(f)
    assert config["gnb"]["bandwidth_mhz"] == 20
    assert config["gnb"]["total_prbs"] == 52
    assert config["latency"]["processing_ms"] == 3.0


def test_run_from_config(capsys):
    run_from_config("examples/config.yaml")
    output = capsys.readouterr().out
    assert "50.00 Mbps" in output
    assert "Near-RT RIC" in output
    assert "CQI 11" in output
