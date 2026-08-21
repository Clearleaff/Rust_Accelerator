# SOLID As An Extraction Discipline

Applied specifically to "move a hot path to Rust and integrate it back," not as
generic OOP trivia. Like `oop-principles.md`, this governs the **host-language
side** of the boundary — the domain code, the service/class the hot path lived
in, and the wrapper. The Rust crate itself is not modeled with SOLID; it
follows `functional-programming-principles.md`. The one exception is
Dependency Inversion below, which is really about the *shape of the boundary*
and therefore has a direct Rust-side counterpart (Rust depends on plain data
types it owns, never on host-framework types).

## S — Single Responsibility
The extracted unit does exactly one computation (e.g. "compute payroll totals for
a batch of records"). It does not also validate permissions, fetch data, or log
audit events. If the candidate function does more than one thing, split it first
in the host language, profile again, and only extract the part that is actually
CPU-bound.

## O — Open/Closed
The core workflow (profile → decide → boundary → implement → validate → report)
and the shared references in this folder are closed for modification per-project.
Language plugins (`django-rust-accelerator`, `spring-rust-accelerator`,
`node-rust-accelerator`, ...) are the extension point — new languages get a new
plugin folder, never a fork of the shared files.

## L — Liskov Substitution
The Rust implementation must be a behavioral drop-in for the Python/Java/JS
original: same output for the same input, including edge cases (nulls, empty
collections, negative numbers, timezone/DST boundaries, duplicate keys). This is
enforced mechanically by the golden/equivalence tests in
`equivalence-and-benchmarking.md` — if those tests don't pass, the Rust path is
not substitutable and must not ship enabled by default.

## I — Interface Segregation
The wrapper function exposes only the parameters the computation actually needs
— not the whole request object, not the whole entity, not the whole settings
object. A narrow, explicit input struct/dict is easier to serialize, easier to
test, and prevents Rust from silently depending on framework internals.

## D — Dependency Inversion
- The host call site depends on an abstraction ("call `calculate_totals(items)`"),
  never on `rust_accelerators` directly. The feature flag / fallback wrapper is
  what implements that abstraction.
- Rust code depends on plain data types it owns, never on host-framework types
  (no Django `Decimal` field objects, no JPA-managed entities, no Node stream
  objects passed by reference).
