# Safe C-ABI Foreign Function Interface (FFI)

This reference outlines patterns for exposing Rust libraries to C/C++ or calling C libraries from Rust.

---

## 1. Data Representation (`#[repr(C)]`)

By default, Rust does not guarantee a stable struct field layout. When exposing or receiving types over FFI, you must specify `#[repr(C)]`:

```rust
#[repr(C)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}
```

---

## 2. Preventing Panics Across the FFI Boundary

Unwinding into foreign code that cannot handle Rust panics is undefined behavior and typically aborts the process. Use `std::panic::catch_unwind`:

```rust
use std::panic;

#[no_mangle]
pub extern "C" fn calculate_metrics(data_ptr: *const f64, len: usize) -> i32 {
    let result = panic::catch_unwind(|| {
        if data_ptr.is_null() {
            return -1;
        }
        // SAFETY: Caller ensures pointer and length are valid
        let slice = unsafe { std::slice::from_raw_parts(data_ptr, len) };
        perform_calculation(slice);
        0
    });

    result.unwrap_or(-99) // Return error code on panic
}
```

---

## 3. String Interoperability

### Passing Strings to C:
```rust
use std::ffi::CString;
use std::os::raw::c_char;

pub fn to_c_string(text: &str) -> Result<*mut c_char, std::ffi::NulError> {
    let c_str = CString::new(text)?;
    Ok(c_str.into_raw()) // Caller in C must free this memory!
}

#[no_mangle]
pub unsafe extern "C" fn free_c_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        // Reconstruct CString to invoke Drop
        drop(CString::from_raw(ptr));
    }
}
```

### Receiving Strings from C:
```rust
use std::ffi::CStr;
use std::os::raw::c_char;

pub unsafe fn parse_c_string(ptr: *const c_char) -> Option<String> {
    if ptr.is_null() {
        return None;
    }
    // SAFETY: Caller guarantees null-terminated C string
    let c_str = CStr::from_ptr(ptr);
    c_str.to_str().ok().map(|s| s.to_string())
}
```

