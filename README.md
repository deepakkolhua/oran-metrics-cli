# \# oran-metrics-cli

# 

# !\[Python](https://img.shields.io/badge/Python-3.10+-blue)

# !\[License](https://img.shields.io/badge/License-MIT-green)

# 

# CLI tool for O-RAN network metric calculations.

# 

# \## Features

# \- Throughput calculator (Mbps)

# \- E2E Latency budget (Near-RT / Non-RT RIC classification)

# \- Spectral Efficiency (bps/Hz)

# \- PRB Utilization

# \- SINR to CQI mapping (3GPP TS 38.214)

# 

# \## Usage

# 

# &#x20;   python src/oran\_metrics/cli.py throughput --bits 50000000 --time 1

# &#x20;   python src/oran\_metrics/cli.py latency --proc 3 --transport 2 --queue 1.5

# &#x20;   python src/oran\_metrics/cli.py cqi --sinr 15.5

# 

# \## Project Structure

# 

# &#x20;   oran-metrics-cli/

# &#x20;   ├── src/oran\_metrics/

# &#x20;   │   ├── \_\_init\_\_.py

# &#x20;   │   ├── calculator.py

# &#x20;   │   └── cli.py

# &#x20;   ├── tests/

# &#x20;   │   └── test\_calculator.py

# &#x20;   ├── docs/

# &#x20;   ├── README.md

# &#x20;   ├── LICENSE

# &#x20;   └── .gitignore

# 

# \## Author

# Deepak Singh - KNU MONET Lab / AutonixAi

