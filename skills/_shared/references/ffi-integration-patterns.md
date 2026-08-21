# FFI / Integration Pattern Catalog

Pick ONE binding strategy per hot path based on the decision tree in
`clean-architecture-and-boundaries.md`. Language plugins reference the row that
applies to their host.

| Host runtime | Preferred in-process binding | Sidecar alternative | Feature flag idiom |
|---|---|---|---|
| Python / Django | PyO3 + maturin | Rust HTTP/gRPC service | Django setting, e.g. `USE_RUST_ACCELERATORS` |
| JVM / Spring Boot | JNI or GraalVM native-image (both brittle to package/ship) — prefer a Rust sidecar unless the team already has JNI tooling | Rust HTTP/gRPC service called via `WebClient`/`RestTemplate` | Spring property + `@ConditionalOnProperty`, e.g. `accelerators.rust.enabled` |
| Node.js / SvelteKit backend | napi-rs or neon native addon | Rust worker process (msgpack/JSON over stdio or a local socket) | env var / config flag, e.g. `USE_RUST_ACCELERATORS=1` |
| Go | cgo (works but reintroduces C-style unsafety) | Rust HTTP/gRPC service | build tag or config flag |

## Why JVM defaults to a sidecar
JNI and GraalVM native-image both work, but packaging/shipping them reliably
across environments (local dev, CI, containers, different JVM vendors) is a
real cost. Unless the team already has that tooling in place, a small Rust
service behind gRPC/HTTP, deployed as its own container, is usually less total
effort than making JNI packaging robust — and it also gives you independent
scaling and easy language-agnostic reuse for other hosts later.

## Wrapper shape (same across all bindings)

```text
def/fun/function calculate_totals(items):
    if not accelerator_enabled():
        return calculate_totals_reference(items)      # existing host code
    try:
        payload = serialize(items)                     # plain data only
        return rust_accelerators.calculate_totals(payload)
    except AcceleratorError:
        log_fallback_event()                            # no payload contents
        return calculate_totals_reference(items)
```

## Serialization guidance
- Prefer the simplest format that preserves the types you actually need:
  in-process bindings (PyO3/napi-rs) can pass native structs directly — use
  that instead of JSON round-tripping when available, it's both faster and
  removes a whole class of serialization bugs.
- For sidecar services, protobuf/gRPC gives you a typed contract; JSON/HTTP is
  fine for lower-throughput or easier-to-debug integrations.
- Always convert money/decimal and datetime/timezone values explicitly at the
  serialization step — never rely on implicit numeric coercion.
