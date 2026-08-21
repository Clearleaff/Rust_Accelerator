# Rust Idioms And Safety Rules

Applies to every crate written under any language plugin. Assume the reader may
be new to Rust — explain ownership/borrowing briefly before generating code that
depends on it, don't assume fluency.

This file covers style and safety mechanics. For how the computation itself
should be *structured* (pure functions, immutability, composition over
loops, algebraic error handling), see
`functional-programming-principles.md` — the two are meant to be read
together: host-language code is OOP/SOLID, Rust code is functional.

## Before writing code
- State in one or two lines who owns the data being processed (the wrapper
  passes ownership in, Rust computes, ownership of the result passes back out).
  This matters because it decides whether you clone, borrow, or move.
- Prefer owned structs (`String`, `Vec<T>`, owned domain structs) at the FFI
  boundary. Do not try to hold a borrowed reference into host-language memory
  across a call — the host runtime (CPython, JVM, V8) does not guarantee that
  memory survives.

## Idiomatic style
- Organize code into modules by domain (`payroll.rs`, `attendance.rs`,
  `reports.rs`), not by "utils.rs" catch-alls.
- Add doc comments (`///`) on every public function explaining what it computes
  and what invariants it assumes about the input.
- Use `Result<T, E>` for anything that can fail; map domain errors to a small
  enum, not raw strings.
- Avoid unnecessary `.clone()` — but don't fight the borrow checker to avoid a
  clone that costs microseconds when the alternative is fighting lifetimes for
  an hour. Correctness and readability first, then tune.

## Hard safety rules (non-negotiable)
- No `unsafe` unless the user explicitly approves it and tests justify it.
- No `.unwrap()`, `.expect()`, panics, or process exits in library code —
  return a typed error instead. A panic across an FFI boundary can crash the
  host process (Python interpreter, JVM, Node process), not just the Rust call.
- Release the GIL/event-loop/thread lock around CPU-heavy pure-Rust
  computation when the binding supports it (PyO3: `py.allow_threads`; Node
  native addons: run on the libuv thread pool, don't block the event loop).
- Keep concurrency explicit. Do not add a thread pool (e.g. Rayon) inside a
  request-handling path without checking the host's worker/concurrency model
  first (e.g. how many Gunicorn/Uvicorn workers, how many JVM threads) —
  uncoordinated parallelism inside an already-parallel host can oversubscribe
  CPU and make things slower.
- Convert `Decimal`/money and datetime values explicitly at the boundary; never
  silently cast money to `f64`.
