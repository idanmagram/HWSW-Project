#!/bin/bash

# Check arguments
if [ $# != 1 ]; then
    echo "Usage: $0 <optimization level [0,1,2]>"
    exit 1
fi

# setup environment
pip install orjson
pip install pyperf
sudo apt install hotspot

# Enable perf
sudo sysctl -w kernel.perf_event_paranoid=-1 && sudo sysctl -w kernel.kptr_restrict=0

# run perf
perf record -e cycles,instructions,cache-misses,cache-references -F 999 -g python3 bm_json_dumps.py --opt_level $1