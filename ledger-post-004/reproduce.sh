#!/usr/bin/env bash
# One command. No model, no API key, no network, no dependency outside python3.
#   ./reproduce.sh
set -euo pipefail
cd "$(dirname "$0")"
python3 run.py
python3 test_suite.py
