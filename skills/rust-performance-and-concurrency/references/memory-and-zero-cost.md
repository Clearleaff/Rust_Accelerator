# Memory Optimization and Zero-Cost Abstractions

This guide covers memory-level optimizations to extract maximum performance from Rust.

---

## 1. Zero-Cost Abstractions

In Rust, "zero-cost abstractions" means:
- What you don't use, you don't pay for.
- What you do use, you couldn't hand code any better.

### Iterators vs Loops
Iterators compile down to pointer arithmetic and SIMD vectorization. In many cases, iterators outperform manual `for` loops with indexing because iterator bounds checks are eliminated at compile time:

```rust
// The compiler optimizes this into vectorized SIMD instructions without bounds checks:
pub fn sum_squares(slice: &[u32]) -> u32 {
    slice.iter().map(|&x| x * x).sum()
}
```

---

## 2. Allocation Optimization Strategies

### 1. Pre-allocate Capacity
Avoid repeated re-allocations as vectors and hash maps grow:

```rust
// Bad: reallocates multiple times
let mut vec = Vec::new();
for i in 0..10_000 {
    vec.push(i);
}

// Good: single heap allocation
let mut vec = Vec::with_capacity(10_000);
for i in 0..10_000 {
    vec.push(i);
}
```

### 2. Clone-on-Write (`Cow<'a, B>`)
When a function frequently returns an unchanged borrow but occasionally needs an owned modified copy, use `Cow`:

```rust
use std::borrow::Cow;

pub fn normalize_whitespace<'a>(input: &'a str) -> Cow<'a, str> {
    if input.contains("  ") {
        Cow::Owned(input.replace("  ", " "))
    } else {
        Cow::Borrowed(input) // zero allocation!
    }
}
```

### 3. Small Buffer Optimization (`SmallVec`)
For collections that are almost always small (e.g. fewer than 8 elements), use crates like `smallvec` to keep items entirely on the stack and only spill to the heap if the threshold is exceeded:

```rust
use smallvec::SmallVec;

// Holds up to 8 items directly on the stack without any heap allocation:
let mut stack_items: SmallVec<[u64; 8]> = SmallVec::new();
stack_items.push(10);
```

---

## 3. Cache Locality and Struct Layout

Modern CPUs rely heavily on L1/L2/L3 cache lines (typically 64 bytes).
- Prefer Structure of Arrays (SoA) over Array of Structures (AoS) when processing a single field across millions of records.
- Flatten deeply nested pointer references.
- Avoid boxing primitives or small structs (`Box<u64>` wastes 8 bytes for the pointer plus heap allocator overhead).

