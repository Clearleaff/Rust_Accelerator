# Traits, Generics, and Type Design in Rust

Rust's type system enables robust domain modeling without classical inheritance.

---

## 1. Traits and Polymorphism

Traits define shared behavior.

### Static Dispatch (`impl Trait` / Generics)
By default, use generic type parameters with trait bounds. The Rust compiler performs monomorphization (generating specialized code for each concrete type), achieving zero runtime overhead:

```rust
pub trait Serializer {
    fn serialize<T: serde::Serialize>(&self, value: &T) -> Result<Vec<u8>, SerializeError>;
}

// Monomorphized, inlined at compile time:
pub fn send_payload<S: Serializer>(serializer: &S, data: &Data) -> Result<(), Error> {
    let bytes = serializer.serialize(data)?;
    transmit(&bytes)
}
```

### Dynamic Dispatch (`dyn Trait`)
Use trait objects when you need heterogeneous collections or to reduce binary size:

```rust
pub trait Plugin: Send + Sync {
    fn name(&self) -> &'static str;
    fn execute(&self) -> Result<(), PluginError>;
}

pub struct PluginManager {
    plugins: Vec<Box<dyn Plugin>>,
}
```

---

## 2. Standard Traits Checklist

For every domain struct or enum you design, consider deriving or implementing:

| Trait | Purpose | When to implement |
| :--- | :--- | :--- |
| `Debug` | Formatted output for debugging (`{:?}`) | Almost all types (`#[derive(Debug)]`) |
| `Clone` | Explicit duplication of data | When duplicating the value is valid |
| `Copy` | Implicit bitwise copy on assignment | Simple stack-only value types |
| `Default` | Sensible default value constructor | Types with reasonable empty states |
| `PartialEq`, `Eq`| Equality comparison (`==`) | Identifiers, keys, records |
| `Hash` | Hashing for `HashMap` / `HashSet` keys | Types used as map keys or set items |
| `Display` | Human-facing formatting (`{}`) | User-visible text and error types |
| `From<T>` / `Into<T>` | Value-to-value type conversion | Natural domain transformations |
| `AsRef<T>` | Borrow-to-borrow conversion | Functions taking path/byte slices |

---

## 3. The Newtype Pattern

Wrap existing types in a tuple struct to prevent logical domain errors:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Milliseconds(pub u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Seconds(pub u64);

impl From<Seconds> for Milliseconds {
    fn from(sec: Seconds) -> Self {
        Milliseconds(sec.0 * 1000)
    }
}
```

This prevents accidental mixing of milliseconds and seconds in timeout signatures.

---

## 4. The Builder Pattern

For types with many optional configuration parameters, provide a fluent builder:

```rust
#[derive(Debug, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub max_connections: usize,
    pub timeout_ms: u64,
}

pub struct ServerConfigBuilder {
    host: String,
    port: u16,
    max_connections: usize,
    timeout_ms: u64,
}

impl ServerConfig {
    pub fn builder(host: impl Into<String>, port: u16) -> ServerConfigBuilder {
        ServerConfigBuilder {
            host: host.into(),
            port,
            max_connections: 1024,
            timeout_ms: 30_000,
        }
    }
}

impl ServerConfigBuilder {
    pub fn max_connections(mut self, limit: usize) -> Self {
        self.max_connections = limit;
        self
    }

    pub fn timeout_ms(mut self, ms: u64) -> Self {
        self.timeout_ms = ms;
        self
    }

    pub fn build(self) -> ServerConfig {
        ServerConfig {
            host: self.host,
            port: self.port,
            max_connections: self.max_connections,
            timeout_ms: self.timeout_ms,
        }
    }
}
```

