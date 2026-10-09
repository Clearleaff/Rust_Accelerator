---
name: rust-performance-and-concurrency
description: Expert skill for writing high-performance, multithreaded, parallel, and asynchronous Rust code. Use when optimizing CPU or memory bottlenecks, using Rayon for data parallelism, using Tokio for async I/O, writing concurrent data structures, or benchmarking with Criterion.
---

# Rust Performance and Concurrency

This skill guides the design and implementation of highly performant, CPU-efficient, and concurrent Rust code.

## Core Rules & Invariants

1. **Measure Before Optimizing**: Never guess where bottlenecks are. Profile with `perf`, `flamegraph`, or microbenchmark with `criterion`.
2. **Zero-Cost Abstractions**: Rust's iterators, closures, and generics optimize into machine code equivalent to (or faster than) hand-tuned C. Prefer idiomatic high-level abstractions first.
3. **Minimize Allocations**: Allocations on the heap have synchronization and cache overhead. Pre-allocate collections with `Vec::with_capacity()`, reuse buffers, and use `Cow<'a, B>` or `SmallVec` where appropriate.
4. **Choose the Right Concurrency Model**:
   - **CPU-bound Batch Work**: Use **Rayon** for data-parallel work-stealing across CPU cores.
   - **I/O-bound Network/Disk**: Use **Tokio** or `async-std` for non-blocking asynchronous event loops.
   - **Never mix blocking/heavy CPU work directly onto async runtime worker threads without `tokio::task::spawn_blocking`**.

---

## 1. Zero-Cost Abstractions and Memory Layout

- **Cache Locality**:
  - Keep related data contiguous in memory. Prefer `Vec<T>` over pointer-heavy linked data structures.
  - Struct layout: Rust reorders struct fields by default to minimize padding and maximize alignment unless `#[repr(C)]` is specified.
- **Avoiding Clones**:
  - Use borrowed slices (`&[T]`, `&str`) instead of passing owned copies.
  - Use `std::borrow::Cow<'a, str>` (Clone-on-Write) when data is usually read without changes but occasionally modified.

See detailed reference: [`references/memory-and-zero-cost.md`](references/memory-and-zero-cost.md)

---

## 2. Data Parallelism with Rayon

- Convert sequential iterator chains directly to parallel iterators using `into_par_iter()`, `par_iter()`, and `par_iter_mut()`:
  ```rust
  use rayon::prelude::*;

  pub fn compute_squares(numbers: &[i64]) -> Vec<i64> {
      numbers
          .par_iter()
          .map(|&x| x * x)
          .collect() // Order is preserved for slice/Vec sources
  }
  ```
- **Chunking**: For micro-computations where per-item work is trivial, group items with `.chunks()` to amortize work-stealing scheduling overhead.
- **Order Preservation**: Note that `par_iter().collect::<Vec<_>>()` maintains input order, but `par_bridge()` does not guarantee ordering.

See detailed reference: [`references/rayon-and-parallelism.md`](references/rayon-and-parallelism.md)

---

## 3. Multithreading Primitives

- **Thread-safe Shared State**:
  - `Arc<Mutex<T>>`: For shared mutable data where contention is low.
  - `Arc<RwLock<T>>`: When reads heavily outnumber writes.
- **Lock-free Atomics**:
  - For single flags or counters, use `std::sync::atomic::{AtomicBool, AtomicUsize}` instead of a `Mutex`.
  - Use `Ordering::Relaxed` for standalone metrics/counters; use `Ordering::Acquire` / `Ordering::Release` when publishing shared data safely across threads.
- **Channels**:
  - Prefer channel-based message passing over shared memory where possible (`crossbeam-channel` or `tokio::sync::mpsc`).

---

## 4. Asynchronous Programming with Tokio

- **Cancellation Safety**:
  - Be mindful of futures dropped mid-execution in `tokio::select!`. Ensure state is consistent if a future is cancelled.
- **Spawn Blocking**:
  - Offload long-running CPU calculations, disk I/O, or blocking library calls from the async worker threads:
  ```rust
  let result = tokio::task::spawn_blocking(move || {
      heavy_cpu_work(&payload)
  }).await??;
  ```

See detailed reference: [`references/async-tokio.md`](references/async-tokio.md)

---

## 5. Benchmarking with Criterion

- Always benchmark before and after optimizations using Criterion:
  ```rust
  use criterion::{black_box, criterion_group, criterion_main, Criterion};

  fn bench_processing(c: &mut Criterion) {
      let data = generate_sample_data(100_000);
      c.bench_function("process_records", |b| {
          b.iter(|| process_records(black_box(&data)))
      });
  }

  criterion_group!(benches, bench_processing);
  criterion_main!(benches);
  ```

See detailed reference: [`references/criterion-benchmarking.md`](references/criterion-benchmarking.md)

