# Functional Programming and Iterators in Rust

Rust combines systems-level efficiency with functional programming paradigms: zero-cost iterator abstractions, pure functions, algebraic data types, and pattern matching.

---

## 1. Iterator Basics

All iterators implement the `Iterator` trait:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
```

Iterators are **lazy**: adapters like `.map()` or `.filter()` do not perform computations until consumed by a terminal consumer (e.g. `.collect()`, `.sum()`, `.for_each()`).

### IntoIterator Flavors

For a collection `c`:
- `c.iter()`: yields shared references `&T`
- `c.iter_mut()`: yields mutable references `&mut T`
- `c.into_iter()`: consumes `c` and yields owned values `T`

---

## 2. Essential Iterator Adapters

| Adapter | Purpose | Example |
| :--- | :--- | :--- |
| `map` | 1-to-1 item transformation | `.map(|x| x * 2)` |
| `filter` | Predicate-based inclusion | `.filter(|x| *x > 0)` |
| `filter_map` | Transforms and filters in one step | `.filter_map(|s| s.parse::<i32>().ok())` |
| `flat_map` | Flattens nested iterators | `.flat_map(|u| u.permissions.iter())` |
| `fold` | Accumulate state across items | `.fold(0, |acc, x| acc + x)` |
| `zip` | Pair elements from two iterators | `a.iter().zip(b.iter())` |
| `enumerate` | Pair each element with its index | `.enumerate()` |
| `take` / `skip`| Slice head or skip items | `.skip(10).take(5)` |

---

## 3. Idiomatic Patterns

### Parse or Filter Cleanly

```rust
pub fn parse_positive_numbers(raw_inputs: &[&str]) -> Vec<u32> {
    raw_inputs
        .iter()
        .filter_map(|s| s.trim().parse::<u32>().ok())
        .filter(|&num| num > 0)
        .collect()
}
```

### Partitioning Data

Split elements into two groups based on a predicate:

```rust
let numbers = vec![1, 2, 3, 4, 5, 6];
let (even, odd): (Vec<i32>, Vec<i32>) = numbers
    .into_iter()
    .partition(|n| n % 2 == 0);
```

### Grouping and Lookups with `fold`

```rust
use std::collections::HashMap;

pub fn count_frequencies<'a>(words: impl IntoIterator<Item = &'a str>) -> HashMap<&'a str, usize> {
    words.into_iter().fold(HashMap::new(), |mut acc, word| {
        *acc.entry(word).or_insert(0) += 1;
        acc
    })
}
```

---

## 4. Pure Functions by Default

Keep core computational logic pure:
- **Determinism**: Same inputs produce identical outputs.
- **No Side Effects**: Do not perform I/O, write to static mutable variables, or log inside compute loops.
- **Separation of Concerns**: Isolate calculations from I/O boundaries:

```rust
// Impure Boundary (I/O, database, networking)
pub async fn handle_batch_request(db: &Database, ids: &[u64]) -> Result<Totals, AppError> {
    let records = db.fetch_records(ids).await?;
    // Pure computation
    let totals = calculate_totals(&records);
    Ok(totals)
}

// Pure Core Logic (easily unit tested and verified)
pub fn calculate_totals(records: &[Record]) -> Totals {
    records
        .iter()
        .fold(Totals::default(), |mut acc, rec| {
            acc.gross += rec.amount;
            acc.tax += rec.tax_rate * rec.amount;
            acc
        })
}
```

