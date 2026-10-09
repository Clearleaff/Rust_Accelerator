---
name: rust-code-writer
description: Comprehensive expert skill for writing idiomatic, safe, and maintainable Rust code. Use whenever authoring, refactoring, or reviewing Rust functions, structs, enums, traits, modules, error handling, or tests.
---

# Idiomatic Rust Code Writer

This skill guides the design and implementation of modern, safe, idiomatic Rust code following industry best practices and the official Rust API guidelines.

## Core Rules & Axioms

1. **Safety & Zero Undefined Behavior First**: Safe Rust by default. Never use `unsafe` unless strictly justified, isolated, documented with `// SAFETY:` invariants, and validated with Miri.
2. **Explicit Over Implicit**: No hidden allocations, no silent type coercion, no invisible mutations.
3. **No Unhandled Failures**: Never use `.unwrap()`, `.expect()`, or `panic!` in library code or hot paths. Use `Result<T, E>` and `Option<T>` with the `?` operator.
4. **Immutability by Default**: Use `let` instead of `let mut`. Reach for `mut` only when an imperative accumulator or in-place mutation clearly improves readability or performance.
5. **Parse, Don't Validate**: Encode invariants directly into the type system using newtypes, typestates, and custom enums.

---

## 1. Ownership, Borrowing, and Memory Rules

- **Take the Least Powerful Type**:
  - Prefer `&str` over `&String` in function arguments.
  - Prefer `&[T]` over `&Vec<T>`.
  - Prefer `impl AsRef<Path>` over `&PathBuf`.
- **Borrow vs Move vs Clone**:
  - If a function only reads data: borrow immutably (`&T`).
  - If a function modifies data in place: borrow mutably (`&mut T`).
  - If a function consumes, transforms, or stores data: take ownership by value (`T`).
  - Avoid unnecessary `.clone()` calls, but do not fight the borrow checker with complex lifetime annotations when a cheap clone at a cold boundary yields clean, maintainable code.
- **Lifetimes**:
  - Rely on lifetime elision where possible.
  - When returning references derived from multiple arguments, explicitly tie the returned lifetime to the input borrow (e.g. `fn find<'a>(needle: &str, haystack: &'a str) -> Option<&'a str>`).
  - Avoid using `'static` as an escape hatch for lifetime mismatches.

See detailed reference: [`references/ownership-and-borrowing.md`](references/ownership-and-borrowing.md)

---

## 2. Expressive Types & Domain Modeling

- **Structs and Enums**:
  - Model mutually exclusive states with data-carrying `enum` variants, never with boolean flags or optional fields inside a struct.
  ```rust
  // Good: State encoded in enum variants
  pub enum PaymentStatus {
      Pending,
      Authorized { transaction_id: String, expires_at: u64 },
      Failed { code: u32, reason: String },
      Completed { receipt_url: String },
  }
  ```
- **Newtype Pattern**:
  - Wrap primitive types to prevent argument transposition errors:
  ```rust
  #[derive(Debug, Clone, PartialEq, Eq, Hash)]
  pub struct UserId(pub u64);

  #[derive(Debug, Clone, PartialEq, Eq, Hash)]
  pub struct OrderId(pub u64);
  ```
- **Typestate Pattern**:
  - Model valid state transitions at compile time:
  ```rust
  pub struct Draft;
  pub struct Published;

  pub struct Post<State> {
      title: String,
      content: String,
      state: std::marker::PhantomData<State>,
  }

  impl Post<Draft> {
      pub fn new(title: String, content: String) -> Self {
          Self { title, content, state: std::marker::PhantomData }
      }
      pub fn publish(self) -> Post<Published> {
          Post { title: self.title, content: self.content, state: std::marker::PhantomData }
      }
  }
  ```

See detailed reference: [`references/traits-and-types.md`](references/traits-and-types.md)

---

## 3. Idiomatic Error Handling

- **Libraries vs Applications**:
  - **Libraries**: Use [`thiserror`](https://docs.rs/thiserror) to define strongly-typed, exhaustive error enums. Never return `Box<dyn Error>` or string errors from library APIs.
  - **Applications/Binaries**: Use [`anyhow`](https://docs.rs/anyhow) for contextual, ergonomic error propagation with `.context("...")`.
- **The `?` Operator**:
  - Propagate errors cleanly. Convert error types using `From`/`Into` implementations or `.map_err()`.
- **No Sentinel Values**:
  - Never use `-1`, `""`, or null pointers to indicate absence. Always return `Option<T>`.

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("file not found at {path}")]
    NotFound { path: String },
    #[error("failed to parse JSON")]
    InvalidJson(#[from] serde_json::Error),
    #[error("io error")]
    Io(#[from] std::io::Error),
}
```

See detailed reference: [`references/error-handling.md`](references/error-handling.md)

---

## 4. Functional Pipelines & Iterators

- **Prefer Iterator Combinators**:
  - Use `map`, `filter`, `filter_map`, `fold`, `flat_map`, `zip`, `chunks`, `windows` instead of manual index loops and mutable accumulators.
- **Short-circuiting and Evaluation**:
  - Iterators are lazy. Chain adapters cleanly and evaluate with terminal operations (`collect`, `sum`, `find`, `any`, `all`).
  - Use `collect::<Result<Vec<_>, _>>()` to turn an iterator of `Result`s into a `Result` of a collection, short-circuiting on the first error.

```rust
pub fn active_user_emails(users: &[User]) -> Vec<&str> {
    users
        .iter()
        .filter(|u| u.is_active)
        .map(|u| u.email.as_str())
        .collect()
}
```

See detailed reference: [`references/functional-iterators.md`](references/functional-iterators.md)

---

## 5. Traits, Generics, and Standard Conventions

- **Derive Standard Traits**:
  - Always derive or implement `Debug`.
  - Derive `Clone`, `Default`, `PartialEq`, `Eq`, `Hash` where semantically meaningful.
- **Implement Standard Conversion Traits**:
  - `Display` for user-facing representation.
  - `From<T>` for lossless conversions (which automatically provides `Into<T>`).
  - `TryFrom<T>` for fallible conversions.
  - `AsRef<T>` for cheap borrowed reference conversions.
- **Static vs Dynamic Dispatch**:
  - Default to generics with trait bounds (`impl Trait` or `where T: Trait`) for zero runtime overhead and compiler inlining.
  - Use trait objects (`Box<dyn Trait>`, `&dyn Trait`) only when heterogeneous collections or dynamic runtime polymorphism are strictly necessary.

---

## 6. Module Organization & Code Quality

- **Module Structure**:
  - Group code by domain / feature modules (`orders.rs`, `users.rs`, `billing.rs`), not by technical layers (`models.rs`, `controllers.rs`, `utils.rs`).
  - Use `pub(crate)` to keep internal helpers hidden from external consumers.
- **Documentation**:
  - Add doc comments (`///`) on all public items with `# Examples`, `# Errors`, and `# Panics` sections where applicable.
- **Testing**:
  - Place unit tests in a nested `#[cfg(test)] mod tests` at the bottom of each file.
  - Place integration tests in a separate `tests/` directory at crate root.
  - Run `cargo clippy --all-targets -- -D warnings` and `cargo fmt` as mandatory checks.

