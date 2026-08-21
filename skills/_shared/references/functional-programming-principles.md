# Functional Programming Discipline For The Rust Side

`oop-principles.md` and `solid-principles.md` govern the **host-language side**
of the boundary (Django/Spring/Node domain code, the wrapper, the class/module
structure that already exists there). They do not apply inside the Rust crate
itself — Rust has no classical inheritance, and forcing OOP class hierarchies
onto it produces unidiomatic, harder-to-verify code. Instead, every Rust
accelerator follows functional principles below. This is also what makes the
equivalence tests in `equivalence-and-benchmarking.md` trustworthy in the
first place.

## Pure functions by default

- The core computation (`fn calculate_totals(items: &[Item]) -> Totals`) should
  be a pure function: same input always produces the same output, no I/O, no
  logging, no global/static mutable state, no reading the clock or the
  filesystem inside it.
- Side effects (timing, error-count metrics) belong in the *wrapper* at the
  boundary, not inside the pure computation. This mirrors the boundary
  contract in `clean-architecture-and-boundaries.md` — plain data in, plain
  data out.
- Pure functions are what makes golden/property tests meaningful: if the
  function can't be trusted to return the same output for the same input,
  equivalence testing against the host-language reference implementation is
  meaningless.

## Immutability by default

- Prefer `let` over `let mut`. Reach for `mut` only when the alternative is
  clearly worse (e.g. building a large `Vec` where a fold would be less
  readable) — not as a default habit carried over from imperative code.
- Avoid interior mutability (`RefCell`, `Cell`, `Mutex` used just to dodge the
  borrow checker) inside the pure computation. If shared mutable state feels
  necessary, that's usually a sign the boundary was drawn wrong — go back to
  `clean-architecture-and-boundaries.md`.
- Treat input slices/references as read-only. The function should never
  mutate data it was handed; it returns new data instead.

## Composition over imperative loops

- Prefer iterator adapters (`map`, `filter`, `fold`, `filter_map`, `zip`,
  `scan`) over hand-written `for` loops with a mutable accumulator, when the
  adapter chain stays readable. Once a transformation needs multiple exit
  conditions or complex branching, a plain loop is fine — clarity beats
  cleverness.
- Build the computation as a small pipeline of composed functions rather than
  one large function with many local mutable variables. Each stage should be
  independently testable.
- Prefer higher-order functions (passing a closure/function as a parameter to
  customize behavior) over building a trait hierarchy to express a variation
  point, unless the variation needs to cross an FFI/dynamic-dispatch boundary.

## Algebraic error and absence handling

- Model "might fail" with `Result<T, E>` and "might be absent" with
  `Option<T>` — never with sentinel values (`-1`, empty string, magic
  numbers) to mean "no value."
- Chain outcomes with combinators (`map`, `and_then`, `ok_or`, `unwrap_or_else`
  — never bare `.unwrap()`/`.expect()`, per `rust-idioms-and-safety.md`)
  instead of nested `if`/early-return checks where that stays readable.
- Keep the error type small and meaningful (a plain enum of the failure modes
  that can actually occur), not a stringly-typed catch-all — this is what the
  wrapper maps to a host-language exception at the boundary.

## Where this stops

Functional style governs the Rust *computation*. It does not mean avoiding
structs, avoiding modules, or avoiding all mutation everywhere — `mut` local
variables inside a tight, well-tested loop are fine when they're clearer than
a combinator chain. The goal is testable, side-effect-free, composable
computation — not FP purism for its own sake.
