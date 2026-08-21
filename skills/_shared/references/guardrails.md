# Rust Rewrite Candidacy Guardrails

## Primary rule

> "A function is a Rust-rewrite candidate only if profiling shows it dominates total request/batch time under realistic load — not merely if it appears CPU-heavy in isolation."

This is not a full Python-to-Rust rewrite program. It is bounded,
evidence-gated, incremental optimization of one verified hotspot at a time.

## Default numeric gate

- Require the candidate to account consistently for at least 15% of
  `total_ms`; prefer 20% as the default project target before accepting the
  cost and risk of an FFI boundary. A project may adjust this threshold during
  Phase 0, but must record the reason before implementation starts.
- Phase 8 must compare both the isolated candidate and end-to-end path under
  identical realistic load. A faster microbenchmark alone does not pass.
- Require improvement above run-to-run noise while preserving the Phase 0
  p50/p95/p99 latency, throughput, CPU, memory, behavioral, API, and
  architecture criteria. Set the precise required gain in Phase 0.
- Include serialization, copying, allocation, conversion, exception mapping,
  and FFI call overhead in the Rust measurement.

## Stop conditions

Stop and document the decision when any condition holds:

- The CPU bottleneck is materially reduced and no longer meets the gate.
- Remaining hotspots are I/O-bound.
- Migration complexity or coupling risk exceeds the expected gain.
- Rust FFI boundary overhead consumes the measured gain.
- The business latency or throughput target is already met.
- Differential behavior, reliability, or rollback requirements cannot be
  satisfied.
