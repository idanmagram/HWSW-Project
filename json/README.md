## JSON dumps benchmarking

### Preparing the machine
`sudo sysctl -w kernel.perf_event_paranoid=-1 && sudo sysctl -w kernel.kptr_restrict=0`

### Running the Benchmark

#### Standard JSON Encoder
`perf record -F 999 -g --call-graph dwarf python3 bm_json_dumps.py --opt_level 0`

#### Optimized Cache JSON Encoder
`perf record -F 999 -g --call-graph dwarf python3 bm_json_dumps.py --opt_level 1`

#### ORJSON library
`perf record -F 999 -g --call-graph dwarf python3 bm_json_dumps.py --opt_level 2`