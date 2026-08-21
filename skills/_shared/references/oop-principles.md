# OOP Discipline For Hot-Path Extraction

These rules apply to the **host-language side** of the boundary — Django,
Spring Boot, Node, or whatever framework owns the domain model — regardless of
which host language is in play. They do not apply inside the Rust crate: Rust
has no classical inheritance, and the Rust computation itself follows
`functional-programming-principles.md` instead. In short: host side stays
OOP/SOLID, Rust side stays functional.

## Encapsulation at the boundary

- The extracted function is a black box: same inputs in, same outputs out, no
  hidden side effects (no DB writes, no cache mutation, no logging of business data).
- Never leak host-language objects (ORM models, JPA entities, Express `req`/`res`,
  Django `request`, framework-managed sessions) across the boundary. Only plain data
  crosses: primitives, lists, maps/dicts, byte buffers, or serialized structs.
- Callers of the wrapper should not need to know Rust is involved. The public
  signature of the original function is preserved unless the user explicitly
  approves a breaking change.

## Abstraction, not duplication

- One abstraction: "accelerated function with a fallback." Every language plugin
  implements this same shape (see `clean-architecture-and-boundaries.md`). Do not
  invent a bespoke pattern per feature.
- Business rules (tax rules, leave-balance rules, pricing rules, permission rules)
  stay modeled in the host language's domain layer. Rust receives *already-resolved*
  data, not raw domain objects it has to interpret.

## Composition over inheritance

- Prefer small, composed Rust functions/structs over deep type hierarchies.
- On the host-language side, prefer wrapping/delegating (decorator-style) over
  subclassing an existing service/class just to swap in the Rust path.

## Immutability at the edge

- Data crossing the FFI/service boundary should be treated as immutable snapshots.
  Mutating shared state from inside Rust (or expecting Rust to mutate host objects
  in place) is a smell — it almost always means the boundary is drawn in the wrong
  place.
