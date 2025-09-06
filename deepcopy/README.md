## Deep Copy benchmarking

git clone https://github.com/idanmagram/HWSW-Project.git
cd HWSW-Project

### Running the Benchmark
perf stat -ddd \
  -e task-clock,cycles,instructions,branches,branch-misses \
  -e cache-references,cache-misses \
  -e L1-dcache-loads,L1-dcache-load-misses \
  -e LLC-loads,LLC-load-misses \
  -e dTLB-loads,dTLB-load-misses,iTLB-loads,iTLB-load-misses \
  -e page-faults,minor-faults,major-faults \
  -- python3-dbg deepcopy/deep_copy_opt_bm_.py

### Creating flame graph

perf report --stdio > perf_report.txt

git clone https://github.com/brendangregg/FlameGraph.git

/root/Flamegraph/stackcollapse-perf.pl out.perf > out.folded

/root/FlameGraph/flamegraph.pl out.folded > flamegraph_copy_opt.svg

