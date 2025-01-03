![perf-tools](https://raw.githubusercontent.com/aayasin/perf-tools/master/perf-tools-logo.png)

[![Python linting](https://github.com/aayasin/perf-tools/actions/workflows/pylint.yml/badge.svg?branch=master)](https://github.com/aayasin/perf-tools/actions/workflows/pylint.yml)

perf-tools is an open-source package that profiles workloads, identifies issues, and maps them to application code.
It is the home for a collection of performance analysis tools, recipes, micro-benchmarks &amp; more

## Overview
* **do.py** -- The main driver with handy shortcuts for setting up and doing profiling, over [Linux perf](https://perf.wiki.kernel.org)
* **study.py** -- A driver to study and compare multiple flavors of an application> E.g. it wraps do.py and employs parallel post-processing, can be used for A-B stats comparison of two configs (-sm 0x4)
* **analyze.py** -- A module for analyzing profiling logs. It automates the process of software optimizations described in [From Top-down Microarchitecture Analysis to Structured Performance Optimizations](https://doi.org/10.52843/cassyni.gtjvgt)
* **pmu.py** -- A module for interface to the Performance Monitoring Unit (PMU)
* **stats.py** -- A module for processing counters and profiling logs
* **tma.py** -- A module with modern encapsulation of the [Top-down Microarchitecture Analysis](http://bit.ly/tma-ispass14) (TMA) method
* **common/** -- common functionality used all over the package
  * **common.py** -- common generic functionality (to be moved here; then this folder can be renamed common1 -> common)
  * **registrar** -- common registry for global names, parameters
* **lbr/** -- functionality for processing Last Branch Record (LBR) streams
  * **loops.py** -- A module for handling loops
  * **funcs.py** -- A module for handling functions / procedures
  * **x86.py** -- A module for handling x86 instructions
* **pmu-tools/** -- linked Andi Kleen's perf-based great tools
  * **toplev** -- profiler featuring TMA method on Intel processors
  * **ocperf** -- perf wrapper that converts Intel event names to perf-events syntax
  * **genretlat** -- a profiler to collect Retire Latencies on recent Intel processors
* **workloads/** -- an evolving collection of "micro-workloads"
  * **aibenchmark.py** -- wraps ai-benchmark use on CPU
  * **BC.sh** -- wrapper of the Linux bc utility
  * **mmm/** -- the matrix-matrix mutiply (mmm) HPC kernel - multiple optimizations as demonstrated in [Tuning Performance via Metrics with Expectations](https://ieeexplore.ieee.org/document/8714063)
  * **src/** -- collection of sources for microbenchmarks
    * **permute.cc** -- calculates permutations of input string. See Makefile, workloads/permute.sh.
* **kernels/** -- an evolving collection of x86 kernels (to be moved under workloads/)
  * **gen-kernel.py** -- generator of X86 kernels
  * **jumpy.py** -- module for different jumping constructs
  * **peakXwide.c** -- sample kernels for a X-wide superscalar machine, e.g. 4 for Skylake
  * **sse2avx.c** -- another auto-generated kernel for SSE <-> AVX ISA transition penalty
  * **memcpy.c** -- a custom kernel for strings of libc demonstrating how to timestamp a region-of-interest
  * **callchain.c** -- a custom kernel for chain of function calls as demonstrated in [Establishing a Base of Trust with Performance Counters for Enterprise Workloads](https://www.usenix.org/system/files/conference/atc15/atc15-paper-nowak.pdf)
  * **pagefault.c** -- a custom kernel for page faults on memory data accesses
  * **fp-arith-mix.c** -- demonstrates utilization of extra counters in Icelake's PMU
  * **rfetch3m** -- a random fetcher across 3MB code footprint (auto-generated)
  * There are more kernels, not listed here and/or produced by **build.py** though not uploaded to git
### Checkout with: 
`git clone --recurse-submodules https://github.com/aayasin/perf-tools`


## Usage
### setting up system (for more robust profiling)
* to setup the perf tool, invoke `./do.py setup-perf`
* to turn-off SMT (CPU hyper-threading), invoke `./do.py disable-smt`; don't forget to re-enable it once done, e.g. `./do.py enable-smt`
* `./do.py disable-prefetches` to disable hardware prefetches. Ditto re-enable comment for this/next commands.
* `./do.py enable-fix-freq` to use fixed-frequency (in paritcular disables Turbo).
* `./do.py disable-atom` to disable E-cores in Hybrid processors.

### profiling
First, edit `run.sh` to invoke your application or use the `-a '<your app and its args>'`, alternatively.
System-wide profiling is supported as well. 
* to profile, simply `./do.py profile` which includes multiple steps:
  * **logging** step: collects the system setup info
  * **basic counting & sampling** steps: collect key metrics like time or CPUs utilized,
    via basic profiling and output top CPU-time consuming commands/modules/functions, 
    their call-stack as well as the disassembly of top hotspot. 
  * **topdown profiling** steps: collect reduced tree, auto drill-down and full-tree collections with multiple re-runs. 
  * **advanced sampling** steps: deeper profiling using advanced capabilities of the PMU, and output certain reports 
    at the assembly level (of hottest command).
    Example reports include instruction-mixes, hitcounts (basic-block execution counts), loops,
    as well as stats on hottest loops (identifying loops has some restrictions). 
    Another precise event step is available but is disabled by default.
  * Additional misc profile-steps are available, e.g. tracing MSRs.
    Refer to [--profile-mask documentation](profile-mask-help.md) for full list of profile-steps.

  A filtered output will be dumped on screen while all logs are saved to the current directory.  
  Use `--profile-mask 42`, as an example, to invoke subset of all steps.  
  For topdown profiling and advanced sampling, see [system requirements](#head3sys).
* `./do.py log` will only log hardware and software setup.
* `./do.py setup-all` will setup all required tool (fetch and build those needed. Internet access required).
* `./do.py setup-perf profile` will setup just perf then do default profiling (multiple commands can be used at once).
* `./do.py tar` will archive all logs into a shareable tar file.
* `./do.py all` will setup perf before doing all above profiling steps.
* `./do.py profile -pm 13a -v1` will do selected profile steps - *per-app counting, sampling, topdown 2-levels,
  sampling w/ LBR* - and print underlying commands as well.
* `./do.py help -m My_Metric` will print description of given metric (that toplev understands)

### kernels (microbenchmarks)
* to build pre-defined ones, simply `cd kernels/ && ./build.py`, or
* `GEN=0 ./build.sh` from kernels/ dir to re-build the kernels without generating them
* to run a kernel, invoke it with number-of-iterations, e.g.
`    ./kernels/jumpy5p14 200000000`
* to create a custom kernel, set the desired parameters. e.g.
`    ./kernels/gen-kernel.py -i PAUSE -n 10`
  outputs a C-file of a loop with 10 PAUSE instructions, that can be fed to your favorite compiler.

### tools
A set of command-line tools to facilitate profiling
* **yperf** -- profiles (system) in one shot, generates reports and advises for SW optimizations
* **slow-branch** -- extracts slow sequences from Timed-LBR profile
* **lbr_stats** -- calculates stats on LBR-based profile
* **lbr_filter** -- filters LBR-based profile on certain IPs
* **lbr/llvm-mca.py** -- calculates IPC-ideal for simple loops using LLVM-mca
* **lbr/uiCA.py** -- calculates IPC-ideal using the uops.info Code Analyzer
* **loop_stats** -- calculates stats for a particular loop in an LBR-based profile
* **ptage** -- computes percentages & sum of number-prefixed input
* **addrbits** -- extracts certain bit-range of hexa input

### wrappers
Shortcuts to set-up required tools or run workloads
* **build-perf.sh** -- builds the perf tool from scratch; invoke with `./do.py build-perf` to let it
    use the installer of your Linux distribution (Ubuntu is the default).
* **build-xed.sh** -- downloads & builds Intel's xed. Enabled by default with `./do.py setup-all --tune :xed:1`.
* **n-copies** -- invokes N-copies of an app, with CPU affinity (uses sibling thread N=2, 1 thread/core when N <= nproc)
* **n-loop** -- run a given app n-times in a loop
* **omp-bin[.sh]** -- wrapper for OpenMP apps setting # of threads and CPU affinity

## More information
### <a name="head3sys">System requirements</a>
Required Linux kernel for most recent processors :tada:  
Intel product | Kernel version | perf version
------------- | -------------- | ------------
Ice Lake | 5.10 |
Rocket Lake | 5.11 |
Alder Lake | 5.13 | 5.17
Raptor Lake | 5.18 |
Sapphire Rapids | 5.18 |
Meteor Lake | 6.4 | 6.3 or 6.5 onwards
Granite Rapids | 6.8 | 6.6 (or 6.12 for Timed PEBS)
Lunar Lake | 6.10 | 6.7

Besides, perf tool version 5.13 or newer is required (except observed [broken perf versions](settings/perf-bad.txt)). See `do.py --install-perf` for more.
