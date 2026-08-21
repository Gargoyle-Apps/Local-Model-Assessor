# Hardware Assessment Method

Use this reference to turn incomplete hardware specifications into explicit ranges. Keep capacity, context, and speed as separate calculations.

## Contents

1. Evidence and confidence
2. Usable model memory
3. Weight-memory estimate
4. KV-cache estimate
5. Decode throughput bound
6. Prefill and batch throughput
7. Multi-accelerator systems
8. Model and workload bands
9. Comparing with the current profile

## 1. Evidence and confidence

Rank evidence in this order:

1. Directly comparable benchmark using the same model, quantization, runtime, context, batch size, and power mode.
2. Comparable benchmark with one documented mismatch.
3. Official specifications plus architecture-aware calculation.
4. Third-party specifications or family-level inference.
5. Unknown.

Assign high, medium, or low confidence to each headline estimate. A precise source value does not make an extrapolation precise.

## 2. Usable model memory

Start with the memory pool the runtime can actually address.

```text
usable_model_memory = addressable_memory - OS/display reserve - runtime reserve - co-run reserve
```

Default only when platform-specific evidence is absent:

- Unified/system memory: reserve the greater of 4 GB or 10% of physical RAM; use more for a desktop workload with browsers, IDEs, containers, or creative applications.
- Dedicated VRAM: reserve 0.5–2 GB for the runtime and display, depending on whether the accelerator also drives the desktop.
- Shared integrated graphics: begin with the smaller of the firmware/driver allocation limit and system RAM after the unified-memory reserve. Mark this low confidence when the limit is unknown.

These are planning defaults, not universal platform limits.

## 3. Weight-memory estimate

Use actual artifact size when a specific model and quant are known. Otherwise estimate resident weights with:

```text
weight_GiB ~= parameters_billions * effective_bytes_per_parameter
```

Practical planning ranges include quantization metadata and common runtime overhead:

| Weight format | Effective GiB per billion parameters |
|---|---:|
| 4-bit class (Q4) | 0.55–0.70 |
| 5-bit class (Q5) | 0.68–0.82 |
| 6-bit class (Q6) | 0.80–0.95 |
| 8-bit class (Q8/INT8) | 1.05–1.20 |
| FP16/BF16 | 2.00–2.20 |

Invert the conservative end to estimate a weights-only ceiling:

```text
maximum_parameters_billions ~= usable_model_memory_GiB / upper_GiB_per_billion
```

Recommend a lower tier after reserving KV cache, graph buffers, multimodal projectors, and concurrency. Architecture and runtime can move real usage outside these ranges.

## 4. KV-cache estimate

Use model metadata when available:

```text
KV_bytes = 2 * layers * context_tokens * KV_heads * head_dimension * KV_element_bytes
```

Multiply by the number of simultaneous sequences. The factor `2` accounts for keys and values. Grouped-query and multi-query attention reduce `KV_heads`; quantized KV reduces `KV_element_bytes`.

Add non-KV context overhead where the runtime exposes it. Vision inputs may consume many prompt tokens. Never use one universal “GB per 4K” number across architectures.

Practical context is the minimum of:

- The model's trained or supported context.
- The runtime's supported context.
- The context that fits after weights and other reserves.
- The context whose prefill latency is acceptable for the job.

## 5. Decode throughput bound

Autoregressive decode is often memory-bandwidth bound at batch 1. A rough upper bound is:

```text
ideal_decode_tokens_per_second ~= effective_memory_bandwidth_GBps / resident_weight_size_GB
```

Apply no universal efficiency factor. Runtime kernels, quant format, cache behavior, CPU/GPU partitioning, prompt length, and power limits vary substantially. If a comparable benchmark is unavailable, present the ideal value only as a ceiling and give a broad practical range or qualitative tier below it.

Do not combine bandwidth numbers from separate memory pools unless one token step can use them in parallel without transfer bottlenecks. PCIe offload usually makes the interconnect or CPU memory path decisive.

## 6. Prefill and batch throughput

Prefill is more compute-sensitive and parallel than single-token decode. Compare:

- Supported matrix formats and usable compute, not marketing TOPS alone.
- Memory capacity for prompt activations and KV cache.
- Runtime/kernel maturity for the accelerator.
- Batch size, prompt length, and power envelope.

State time-to-first-token separately from decode speed. For server use, distinguish per-user latency from aggregate tokens per second.

## 7. Multi-accelerator systems

- Capacity is not additive unless the runtime shards the model.
- Decode speed may fail to scale when the interconnect is slower than local memory.
- Replication increases concurrency but not the largest model that one worker can load.
- Consumer multi-GPU configurations need explicit evidence for topology, peer access, runtime support, and power/cooling.

## 8. Model and workload bands

Use parameter bands as examples, not quality rankings:

| Resident model tier | Typical local use |
|---|---|
| Sub-4B | Autocomplete, extraction, routing, compact vision, edge tasks |
| 7B–14B | Responsive chat, coding assistance, tool use, RAG synthesis |
| 20B–35B | Stronger coding/reasoning, higher-quality drafting, usually lower concurrency |
| 40B–70B | Quality-focused work, long batch jobs, or premium-memory systems |
| Above 70B | Specialized high-memory or sharded deployments |

Model architecture, training quality, quantization sensitivity, and task fit matter as much as parameter count. A sparse MoE can decode faster than a dense model with the same total parameters, but its full weights normally still need to reside in memory.

## 9. Comparing with the current profile

Use `vram_budget.total_available - vram_budget.os_headroom_gb` as the current profile's declared effective budget when both values exist. Treat `hardware_classes.*.tps_range` as profile assumptions unless the profile explicitly marks them as measured.

Calculate ratios only for like-for-like quantities:

- Capacity ratio: target usable model memory / current effective budget.
- Bandwidth ratio: target bandwidth / current bandwidth, only when both refer to the active model-memory path.
- Benchmark ratio: target score / current score, only for matching benchmark conditions.

Do not average these ratios into a synthetic score.
