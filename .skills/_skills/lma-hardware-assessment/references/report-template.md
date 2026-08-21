# Hardware Assessment Report Template

Adapt the sections to the question. Omit empty sections rather than filling them with guesses.

## Verdict

State who should buy or use this configuration, the strongest model tier it runs comfortably, and its main limiting factor.

## Configuration assessed

| Component | Specification | Confidence/source |
|---|---|---|
| CPU | | |
| Accelerator | | |
| Memory topology and capacity | | |
| Memory bandwidth | | |
| Storage / interconnect | | |
| Power / cooling configuration | | |

Call out variant ambiguity immediately below the table.

## Model capacity and context

| Model/quant tier | Weights estimate | Practical context | Concurrency | Fit |
|---|---:|---:|---|---|
| | | | | Strong / Workable / Poor / Unknown |

State usable-memory reserve, KV-cache assumptions, and whether the context is model-supported.

## Expected performance

Separate:

- Prompt ingestion / time to first token.
- Batch-1 decode tokens per second.
- Aggregate serving throughput, when relevant.

Give ranges and confidence. Put any specification-derived ceiling next to, but never in place of, an expected practical range.

## Workload fit

| Workload | Fit | Why / constraint |
|---|---|---|
| Interactive chat and coding | | |
| Long-context or RAG | | |
| Agents / concurrent services | | |
| Vision / multimodal | | |
| Embeddings / reranking | | |
| Media generation or transcription | | |
| Fine-tuning | | |

## Optional comparison with current hardware

Include only when the local profile exists and has comparable fields.

| Dimension | Proposed hardware | Current profile | Practical difference |
|---|---:|---:|---|
| Usable model memory | | | |
| Memory bandwidth | | | |
| Recommended model tier | | | |
| Context / concurrency | | | |
| Runtime support | | | |

Do not expose the profile's machine name or identifiers.

## Caveats and confidence

List the few assumptions most likely to change the verdict. End with the benchmark, missing specification, or exact configuration detail that would most reduce uncertainty.
