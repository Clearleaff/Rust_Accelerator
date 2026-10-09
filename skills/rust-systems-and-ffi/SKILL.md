---
name: rust-systems-and-ffi
description: Expert skill for systems-level Rust programming, writing sound unsafe blocks, raw pointer manipulation, C-ABI FFI boundaries, and PyO3/NAPI bindings. Use when interacting with OS APIs, external libraries, foreign runtimes, or detecting undefined behavior with Miri.
---

# Rust Systems Programming and FFI

This skill guides the implementation of low-level systems code, sound `unsafe` blocks, and Foreign Function Interfaces (FFI).

## Core Rules & Non-Negotiable Invariants

1. **Uphold the Unsafe Contract**: `unsafe` does not disable the borrow checker; it grants five superpowers (dereferencing raw pointers, calling unsafe functions, implementing unsafe traits, mutating mutable statics, accessing union fields). You must manually maintain compiler invariants.
2. **Mandatory Safety Documentation**: Every `unsafe fn` must have a `# Safety` section in its doc comment explaining the callers' prerequisites. Every `unsafe` block must be preceded by a `// SAFETY:` comment justifying why the invariants hold.
3. **Never Panic Across FFI**: A panic unwinding past an `extern "C"` boundary is undefined behavior and aborts or corrupts host runtimes. Always wrap FFI entrypoints in `std::panic::catch_unwind`.
4. **Audit with Miri**: Test every `unsafe` implementation with Miri (`cargo miri test`) to detect aliasing violations, use-after-free, memory leaks, and unaligned accesses.

---

## 1. Writing Sound `unsafe` Rust

- **Raw Pointers**:
  - `*const T` (immutable raw pointer) and `*mut T` (mutable raw pointer).
  - Creating raw pointers is safe; **dereferencing** them is `unsafe`.
  - Validate non-nullness (`ptr.is_null()`) and alignment (`ptr.is_aligned()`) before dereferencing.
- **Uninitialized Memory**:
  - Never use `std::mem::uninitialized()` (deprecated and immediate UB).
  - Use `std::mem::MaybeUninit<T>` when populating uninitialized buffers.
- **Aliasing Rules (Stacked Borrows / Tree Borrows)**:
  - You must never create two simultaneous `&mut T` references pointing to overlapping memory, even via raw pointer casts.

See detailed reference: [`references/unsafe-and-miri.md`](references/unsafe-and-miri.md)

---

## 2. C-ABI FFI Boundaries

- **Layout Compatibility**:
  - Use `#[repr(C)]` on all structs and enums that cross the FFI boundary.
  - Use fixed-width integer types (`u8`, `u32`, `i64`, `usize`) rather than platform-variable types.
- **String Handling**:
  - Use `std::ffi::CStr` to inspect null-terminated strings passed from C without copying.
  - Use `std::ffi::CString` when creating null-terminated strings in Rust to pass to C.
- **Exporting Functions**:
  ```rust
  #[no_mangle]
  pub extern "C" fn calculate_sum(ptr: *const i32, len: usize) -> i64 {
      if ptr.is_null() {
          return 0;
      }
      // SAFETY: Caller guarantees ptr points to len valid contiguous i32 values
      let slice = unsafe { std::slice::from_raw_parts(ptr, len) };
      slice.iter().map(|&x| x as i64).sum()
  }
  ```

See detailed reference: [`references/c-ffi-boundaries.md`](references/c-ffi-boundaries.md)

---

## 3. High-Level Language Bindings (PyO3)

- **Ownership Across Boundaries**:
  - Host language garbage collectors do not follow Rust lifetimes. Extract data into Rust-owned types (`Vec<T>`, `String`, plain structs) at the boundary.
  - Use PyO3's modern `Bound<'py, T>` for attached references and `Py<T>` for thread-safe handles.
- **GIL Management**:
  - Release the Python GIL around CPU-heavy pure Rust computations using `py.detach(|| { ... })` (formerly `allow_threads`).

See detailed reference: [`references/pyo3-bindings.md`](references/pyo3-bindings.md)

