#!/usr/local/bin/python

import sys
sys.stdout = open("/golem/output/benchmark.log", "w")

import ai_benchmark
benchmark = ai_benchmark.AIBenchmark()
results = benchmark.run_inference()

sys.stdout.close()
