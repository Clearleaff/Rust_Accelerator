# Equivalence Testing And Benchmarking

Every extraction ships with both, before it is ever enabled by default.

## Behavioral contract before migration

- Write black-box tests before Rust code. Assert only input to observable
  output, exception, ordering, or external side effect; never assert which
  implementation ran or how it is structured.
- Cover normal, boundary, invalid, empty/null, Unicode, large-payload, error,
  and ordering behavior.

## Golden / differential tests

- Run the same inputs through the host-language reference implementation and
  the Rust path; assert identical output.
- Cover: empty input, null/None/nil fields, duplicate keys/records, negative
  numbers, very large batches, leap years and DST/timezone boundaries,
  malformed/partial records, and permission/authorization edge cases if the
  original function touched them before extraction.
- Where arithmetic, grouping, ordering, or date-range logic is complex, add
  property-style tests (e.g. `hypothesis` for Python, `proptest` for Rust,
  `jqwik` for Java, `fast-check` for JS/TS) rather than only example-based
  tests.
- Preserve ordering guarantees the caller depends on, even if the old code's
  ordering was an accident of Python dict/list or Java `HashMap` iteration —
  make it explicit and tested going forward.

## Benchmarking

- Before migration, capture median, p95, throughput, CPU, and relevant memory
  for the unchanged host implementation. Also capture end-to-end p50/p95/p99,
  throughput, CPU, and memory for the containing request or batch path.
- Benchmark realistic input sizes (production-scale batches), not just toy
  examples.
- Run host-only and host+Rust on the same hardware, workload, process model,
  warmup policy, and tool versions. Include all FFI conversion/call overhead.
- Report wall time, throughput, CPU, and relevant memory before/after. State
  the benchmark command, environment, input shape, and raw result location so
  results are reproducible.
- If benchmarking genuinely cannot be run (e.g. no representative data
  available), say so explicitly in the final report rather than omitting the
  section.

## Rollout gate

- Do not flip the feature flag to default-on until: equivalence tests pass,
  a benchmark shows a real improvement, and the fallback path has been
  exercised by a test that simulates the Rust extension failing/being
  unavailable.
- Apply the candidacy and stop rules in `guardrails.md`. Insignificant gains
  produce a documented stop decision.
