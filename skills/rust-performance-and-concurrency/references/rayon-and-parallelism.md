# Data Parallelism with Rayon

Rayon is Rust's premier data parallelism library. It uses a lightweight work-stealing scheduler to distribute iterator tasks across all available CPU cores.

---

## 1. When to Use Rayon

- **Use Rayon for**:
  - CPU-bound computations iterating over collections (e.g. mathematical transformations, parsing large files in memory, hashing batches of items).
  - Bulk sorting (`par_sort()`, `par_sort_unstable()`).
- **Do NOT use Rayon for**:
  - I/O-bound tasks (network calls, database queries) — use Tokio instead.
  - Small collections (<1,000 trivial elements) where thread communication overhead outweighs execution time.
  - Inside heavily multi-worker processes (like 32-worker web servers) where thread pool oversubscription can starve the machine.

---

## 2. Basic Rayon Patterns

Add to `Cargo.toml`:
```toml
[dependencies]
rayon = "1.10"
```

### Parallel Map & Collect

```rust
use rayon::prelude::*;

pub fn process_data(records: &[Record]) -> Vec<TransformedRecord> {
    records
        .par_iter()
        .map(|r| transform(r))
        .collect() // Reassembles in exact original order
}
```

### Parallel Filtering and Reduction

```rust
use rayon::prelude::*;

pub fn sum_large_dataset(values: &[f64]) -> f64 {
    values
        .par_iter()
        .filter(|&&v| v.is_finite())
        .sum()
}
```

---

## 3. Order Preservation

| Operation | Preserves Sequence Order? | Performance Note |
| :--- | :--- | :--- |
| `par_iter().collect::<Vec<_>>()` | **Yes** | Built-in indexed slice reconstruction |
| `par_bridge()` | **No** | Used to convert sequential iterators to parallel |
| `par_iter().for_each()` | **No** | Executes in whichever thread finishes first |

---

## 4. Custom Thread Pool Configuration

When integrating Rayon into a larger system with restricted core allocations:

```rust
use rayon::ThreadPoolBuilder;

let pool = ThreadPoolBuilder::new()
    .num_threads(4)
    .build()
    .unwrap();

pool.install(|| {
    // Operations inside this closure use the custom 4-thread pool
    data.par_iter().map(expensive_step).collect::<Vec<_>>()
});
```

