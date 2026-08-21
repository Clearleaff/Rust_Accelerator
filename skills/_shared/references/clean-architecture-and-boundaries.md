# Architecture: Extracting A Hot Path Into Rust

This is the language-agnostic decision tree and boundary contract. Language
plugins inherit this and only add framework-specific vocabulary (e.g. what
"the ORM" or "the request object" means in that stack).

## Decision tree

Choose the smallest architecture that solves the *measured* bottleneck:

- **Host-language-only optimization** — query count, indexes, caching, batching,
  serialization shape, or template/render work dominates. Fix it there; do not
  reach for Rust.
- **In-process native extension** (PyO3/maturin for Python, napi-rs/neon for
  Node, JNI/GraalVM native-image for Java) — hot work is CPU-bound and called
  synchronously inside a request handler, command, or worker, and process
  startup cost matters.
- **Rust sidecar service** (HTTP/gRPC, same host or same pod) — job is
  long-running, independently scalable, shared across multiple apps/services,
  or the native-extension toolchain is too heavy for the target runtime (this
  is often the pragmatic default for JVM hosts, where JNI packaging is brittle).
- **Rust CLI helper** — offline import/export/report pipelines where process
  startup cost is acceptable and the host just shells out.

## Recommended layout (language plugin fills in `<host_app>`)

```text
rust/
  <project>_accelerators/
    Cargo.toml
    <build manifest for chosen binding: pyproject.toml | napi config | build.gradle glue>
    src/
      lib.rs
      <domain_a>.rs
      <domain_b>.rs

<host_app>/
  accelerators.<ext>      # wrapper module, call sites never import Rust directly
  tests/
    test_<feature>_accelerator.<ext>
```

## Boundary contract (the same 6 steps in every language plugin)

1. The existing host-language function remains as the reference implementation.
   It is never deleted in the same change that introduces Rust.
2. A wrapper receives the *same input* the old call site already had.
3. The wrapper converts host objects (ORM models, entities, request bodies) to
   plain data before crossing the boundary.
4. Rust computes using only plain structs/data and returns plain output.
5. The wrapper converts the output back to the exact shape callers already
   expect.
6. A feature flag decides Rust path vs. host-language fallback, and any Rust
   exception falls back to the host implementation rather than propagating a
   Rust-internal error to the end user.

## Observability

Add lightweight timing around the wrapper boundary while validating rollout:
input size, fallback-usage count, Rust exception count, elapsed-time bucket.
Never log the sensitive payload itself — see
`security-and-privacy-guardrails.md`.
