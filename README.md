# oran-metrics-cli

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-10%20passed-brightgreen)

CLI tool for O-RAN network metric calculations.

## Install

    git clone https://github.com/deepakkolhua/oran-metrics-cli.git
    cd oran-metrics-cli
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .

## Usage

### Individual commands

    oran-metrics throughput --bits 50000000 --time 1
    oran-metrics latency --proc 3 --transport 2 --queue 1.5
    oran-metrics cqi --sinr 15.5

### Run all metrics from YAML config

    oran-metrics run --config examples/config.yaml

### Example output

    === SemDT-RAN Phase 1 ===
    Throughput:    50.00 Mbps
    Spectral Eff:  2.50 bps/Hz
    PRB Util:      86.5%
    SINR 15.5 dB -> CQI 11
    E2E Latency:   6.50 ms (Near-RT RIC compatible)

## Run tests

    pytest tests/ -v

## Project structure

    oran-metrics-cli/
    ├── src/oran_metrics/
    │   ├── __init__.py
    │   ├── calculator.py
    │   ├── cli.py
    │   └── config_runner.py
    ├── tests/
    │   ├── test_calculator.py
    │   └── test_config_runner.py
    ├── examples/
    │   └── config.yaml
    ├── pyproject.toml
    ├── requirements.txt
    ├── LICENSE
    └── .gitignore

## Author

Deepak Singh - KNU MONET Lab / AutonixAi
