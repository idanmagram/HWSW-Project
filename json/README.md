## JSON dumps benchmarking

### Preparing the machine
`sudo sysctl -w kernel.perf_event_paranoid=-1 && sudo sysctl -w kernel.kptr_restrict=0`

### Running the Benchmark

#### Standard JSON Encoder
`perf record -e cycles,instructions,cache-misses,cache-references -F 999 -g python3 bm_json_dumps.py --opt_level 0`

#### Optimized Cache JSON Encoder
`perf record -e cycles,instructions,cache-misses,cache-references -F 999 -g python3 bm_json_dumps.py --opt_level 1`

#### ORJSON library
`perf record -e cycles,instructions,cache-misses,cache-references -F 999 -g python3 bm_json_dumps.py --opt_level 2`

### Creating Flamegraph
`hotspot perf.data`

### More detailed Flamegraph
To get full stack, run perf record with `--call-graph dwarf`