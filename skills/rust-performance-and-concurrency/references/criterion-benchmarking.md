# Benchmarking and Profiling Rust Code

Criterion is a statistics-driven benchmarking framework for Rust that detects performance regressions and improvements with statistical rigor.

---

## 1. Setup

Add Criterion to `Cargo.toml`:

```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "compute_benchmark"
harness = false
```

Create `benches/compute_benchmark.rs`:

```rust
use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use my_crate::{algorithm_a, algorithm_b};

fn bench_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("Algorithms");
    let input_sizes = [100, 1_000, 10_000];

    for size in input_sizes {
        let data: Vec<i64> = (0..size).collect();

        group.bench_with_input(BenchmarkId::new("AlgorithmA", size), &data, |b, d| {
            b.iter(|| algorithm_a(black_box(d)))
        });

        group.bench_with_input(BenchmarkId::new("AlgorithmB", size), &data, |b, d| {
            b.iter(|| algorithm_b(black_box(d)))
        });
    }

    group.finish();
}

criterion_group!(benches, bench_comparison);
criterion_main!(benches);
```

---

## 2. Preventing Compiler Optimization Tricks

- **`black_box(...)`**: Prevents the compiler from dead-code-eliminating computations whose results are never read or constant-folding predetermined arguments.

---

## 3. Running Benchmarks

```bash
# Run benchmarks
cargo bench

# Run a specific benchmark
cargo bench --bench compute_benchmark -- Algorithms/AlgorithmA
```

Criterion outputs statistical confidence intervals (mean, median, p95) and compares against previous runs, highlighting regressions in red and improvements in green.
HTML reports are generated at `target/criterion/report/index.html`.

