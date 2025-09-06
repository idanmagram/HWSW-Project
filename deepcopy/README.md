## Deep Copy benchmarking

### Running the Benchmark
perf stat -ddd \
  -e task-clock,cycles,instructions,branches,branch-misses \
  -e cache-references,cache-misses \
  -e L1-dcache-loads,L1-dcache-load-misses \
  -e LLC-loads,LLC-load-misses \
  -e dTLB-loads,dTLB-load-misses,iTLB-loads,iTLB-load-misses \
  -e page-faults,minor-faults,major-faults \
  -- python3-dbg HWSW-Project/deepcopy/deep_copy_opt_bm_.py
