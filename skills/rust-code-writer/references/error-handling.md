# Error Handling in Production Rust

Rust distinguishes between **recoverable errors** (handled via `Result<T, E>`) and **unrecoverable errors** (handled via `panic!`).

## 1. Golden Rules of Error Handling

1. **Zero Panics in Libraries**: Never invoke `panic!`, `.unwrap()`, or `.expect()` in library code, public APIs, or long-running worker loops.
2. **Explicit Error Types**: Represent distinct failure modes with enum variants.
3. **Preserve Context**: Always propagate original source errors and attach situational context when bubbling errors up.

---

## 2. Library Errors with `thiserror`

Use `thiserror` for domain and library crates. It generates `std::error::Error` and `Display` implementations automatically:

```rust
use std::io;
use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DatabaseError {
    #[error("failed to connect to host '{host}': {source}")]
    ConnectionFailed {
        host: String,
        #[source]
        source: io::Error,
    },

    #[error("record with id {id} not found in table '{table}'")]
    RecordNotFound { table: &'static str, id: u64 },

    #[error("query timed out after {timeout_secs}s")]
    Timeout { timeout_secs: u64 },

    #[error("invalid migration schema version {0}")]
    InvalidSchemaVersion(u32),
}
```

### Deriving `From` with `#[from]`

```rust
#[derive(Error, Debug)]
pub enum StorageError {
    #[error("I/O error")]
    Io(#[from] std::io::Error),

    #[error("Serialization error")]
    Serialization(#[from] serde_json::Error),
}
```
Functions can return `Result<T, StorageError>` and use `?` on `std::io::Error` or `serde_json::Error` seamlessly.

---

## 3. Application Errors with `anyhow`

In application roots, CLI binaries, or top-level request handlers where handling specific error variants is not required, use `anyhow::Result`:

```rust
use anyhow::{Context, Result};
use std::fs;

fn load_server_config(path: &str) -> Result<Config> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("failed to read configuration file at '{path}'"))?;

    let config: Config = toml::from_str(&content)
        .with_context(|| format!("malformed TOML in configuration file '{path}'"))?;

    Ok(config)
}
```

---

## 4. Working with `Option<T>` and Combinators

Avoid nested `match` statements when transforming `Option` and `Result`:

### Common Combinators

- `.map(|v| ...)`: Transform the inner value if `Some`/`Ok`.
- `.and_then(|v| ...)`: FlatMap when the transform function itself returns an `Option`/`Result`.
- `.ok_or(error)` / `.ok_or_else(|| ...)`: Convert `Option<T>` to `Result<T, E>`.
- `.unwrap_or(default)` / `.unwrap_or_else(|| ...)`: Provide a fallback value safely.

```rust
// Converting Option to Result with the ? operator
pub fn get_user_email(user_id: u64) -> Result<String, UserError> {
    let user = find_user(user_id).ok_or(UserError::UserNotFound(user_id))?;
    let email = user.email.ok_or(UserError::MissingEmail(user_id))?;
    Ok(email)
}
```

---

## 5. Converting Collections of Results

To convert an iterator yielding `Result<T, E>` into a single `Result<Vec<T>, E>` that short-circuits on the first failure:

```rust
let ids = vec![1, 2, 3, 4];
let results: Result<Vec<Record>, DbError> = ids
    .into_iter()
    .map(|id| fetch_record(id))
    .collect(); // stops at first Err and returns it
```

