# Writing Sound Unsafe Rust and Validating with Miri

Rust's type system provides compile-time memory safety guarantees. `unsafe` is used when implementing low-level primitives where the compiler cannot automatically verify invariants.

---

## 1. The Contract of `unsafe`

Using `unsafe` does not disable Rust's safety rules; it places the responsibility on the programmer to prevent **Undefined Behavior (UB)**.

### Examples of Undefined Behavior to Avoid:
- Dereferencing null, dangling, or unaligned pointers.
- Violating the pointer aliasing model (creating simultaneous mutable references to the same memory).
- Reading uninitialized memory.
- Producing invalid primitive values (e.g. `bool` that is neither 0 nor 1, invalid `char` code points, invalid enum discriminant).
- Data races across concurrent threads.
- Unwinding across an `extern "C"` boundary.

---

## 2. Safety Comments Protocol

Every `unsafe` item must be explicitly justified:

```rust
pub struct RingBuffer<T> {
    buf: *mut T,
    capacity: usize,
    head: usize,
    tail: usize,
}

impl<T> RingBuffer<T> {
    /// Reads the element at `index`.
    ///
    /// # Safety
    ///
    /// `index` must be strictly less than `self.capacity` and the slot
    /// must contain an initialized value.
    pub unsafe fn get_unchecked(&self, index: usize) -> &T {
        // SAFETY: The caller verified index < self.capacity and slot is initialized.
        // self.buf is guaranteed aligned and allocated for self.capacity elements.
        &*self.buf.add(index)
    }
}
```

---

## 3. Safe Initialization with `MaybeUninit<T>`

```rust
use std::mem::MaybeUninit;

pub fn initialize_buffer() -> [u32; 1024] {
    // Create an uninitialized array safely:
    let mut data: [MaybeUninit<u32>; 1024] = unsafe {
        MaybeUninit::uninit().assume_init()
    };

    for (i, elem) in data.iter_mut().enumerate() {
        elem.write(i as u32 * 2);
    }

    // SAFETY: All 1024 elements have been initialized above.
    unsafe { std::mem::transmute::<_, [u32; 1024]>(data) }
}
```

---

## 4. Validating with Miri

Miri is an interpreter that executes Rust intermediate representation (MIR) and verifies that no undefined behavior occurs.

### Installing and Running Miri:

```bash
rustup component add miri
cargo miri test
```

Miri checks for:
- Out-of-bounds pointer arithmetic and memory accesses.
- Stacked Borrows / Tree Borrows aliasing model violations.
- Memory leaks in tests.
- Use-after-free and use-after-scope.

