# High-Performance Python Extensions with PyO3

PyO3 allows compiling Rust code into native Python extension modules that can be called like standard Python packages.

---

## 1. Project Configuration

In `Cargo.toml`:

```toml
[package]
name = "rust_accelerator"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_accelerator"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
rayon = "1.10"
```

---

## 2. Safe Extraction and Detaching the GIL

The key to high performance is extracting data into Rust-owned types before releasing the GIL:

```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
pub fn process_data(py: Python<'_>, raw_values: Vec<f64>) -> PyResult<Vec<f64>> {
    // Release the Global Interpreter Lock for CPU-bound computations:
    let result = py.detach(|| {
        raw_values
            .par_iter()
            .map(|&x| (x * 2.5).sin())
            .collect::<Vec<f64>>()
    });

    Ok(result)
}

#[pymodule]
fn rust_accelerator(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_data, m)?)?;
    Ok(())
}
```

---

## 3. Core Boundaries Rules

1. **Extract Immediately**: Extract Python objects into owned Rust structs at the function signature level.
2. **Never Touch Python Objects Inside `detach`**: `py.detach` (or `allow_threads`) requires the closure to be `Ungil`. Never access `Bound<'py, T>` inside the detached block.
3. **Map Errors Explicitly**: Return `PyResult<T>` and map Rust error enums into appropriate Python exceptions:
   ```rust
   use pyo3::exceptions::PyValueError;

   fn validate(input: i32) -> PyResult<()> {
       if input < 0 {
           return Err(PyValueError::new_err("Input cannot be negative"));
       }
       Ok(())
   }
   ```

