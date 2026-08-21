---
title: "The Complete Rust and PyO3 Guide: Ownership, Borrowing, Lifetimes, and Building Python Accelerators"
description: "A complete, detailed reference covering Rust fundamentals (ownership, borrowing, lifetimes, structs, enums, Option) through CPython's memory model, PyO3 bindings, and safe multithreading, for engineers building Rust accelerators for Python."
keywords: ["Rust ownership and borrowing explained", "Rust lifetimes tutorial", "PyO3 complete guide", "CPython GIL and reference counting", "Rust for Python developers", "build Rust accelerator for Python", "Rust structs and enums", "Rust Option type"]
---

# The Complete Rust and PyO3 Guide: Ownership, Borrowing, Lifetimes, and Building Python Accelerators

This guide is a complete reference for engineers who already work with Python in production and are learning Rust specifically to accelerate CPU-bound code. It starts from an absolute beginner baseline in Rust and builds up to a production pattern for calling Rust from Python safely. It is written as a reference to return to, not a single linear read.

For a focused deep dive on Rayon's threading model and the specific cases where it should not be used, see the companion article: **[Rayon in Rust: How Threading Works and When You Should Never Use It as an Accelerator](https://your-blog-domain.example.com/rayon-threading-guide)**

## Table of Contents

1. Setup and the cargo workflow
2. Variables and immutability by default
3. Basic data types and functions
4. Ownership
5. Borrowing and references
6. Lifetimes
7. Structs
8. Enums and the Option type
9. CPython memory management: reference counting and the GIL
10. PyO3: bridging Rust and Python
11. Extraction versus reference: the safety boundary
12. Rayon and safe parallelism
13. The complete production pattern
14. Common mistakes
15. Conclusion

## 1. Setup and the Cargo Workflow

Rust is installed through rustup, which manages the compiler (`rustc`) and the build tool and package manager (`cargo`).

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo new my_project
cd my_project
cargo run
```

`cargo new` scaffolds a project with `src/main.rs` and a `Cargo.toml` manifest, the equivalent of a `package.json` or `pom.xml`. `cargo run` compiles and executes the project in one step.

## 2. Variables and Immutability by Default

Every variable in Rust is immutable unless explicitly marked otherwise. This is a deliberate design choice: mutability is treated as the exception, not the default.

```rust
fn main() {
    let x = 5;
    x = 6; // compile error: cannot assign twice to immutable variable
}
```

Adding `mut` makes the intent explicit and enables reassignment.

```rust
let mut x = 5;
x = 6; // fine
```

Constants, declared with `const`, are always immutable and always require an explicit type annotation, unlike `let`, where the compiler can infer the type.

```rust
const MAX_POINTS: u32 = 100_000;
```

Rust also supports shadowing, where a new `let` binding reuses a name and can even change its type, which is distinct from mutation:

```rust
let spaces = "   ";
let spaces = spaces.len(); // a new binding, now a number
```

## 3. Basic Data Types and Functions

Scalar types include signed and unsigned integers (`i8` through `i128`, `u8` through `u128`), floating point numbers (`f32`, `f64`), booleans, and characters. The default integer type is `i32` and the default float type is `f64` when no annotation is given.

Compound types include tuples, which are fixed-size and can mix types, and arrays, which are fixed-size and hold a single type.

```rust
let tup: (i32, f64, bool) = (500, 6.4, true);
let arr: [i32; 5] = [1, 2, 3, 4, 5];
```

Functions return the value of their final expression when that expression has no trailing semicolon. Adding a semicolon turns an expression into a statement, which returns nothing.

```rust
fn add(x: i32, y: i32) -> i32 {
    x + y // no semicolon: this is the return value
}
```

## 4. Ownership

Ownership is the mechanism that gives Rust memory safety without a garbage collector. Three rules govern it.

1. Every value has exactly one owner, which is a variable.
2. There can only be one owner at a time.
3. When the owner goes out of scope, the value is dropped and its memory is freed.

```rust
fn main() {
    {
        let s = String::from("hello");
        println!("{}", s);
    } // s goes out of scope here and is dropped automatically
}
```

### Move semantics

Heap-allocated types such as `String` and `Vec` do not implement the `Copy` trait. Assigning one variable to another moves ownership rather than copying data.

```rust
let s1 = String::from("hello");
let s2 = s1; // ownership moves from s1 to s2
println!("{}", s1); // compile error: value borrowed here after move
```

This prevents a double free: if both `s1` and `s2` owned the same heap allocation, both would attempt to free it when their scopes ended.

Stack-only types such as integers, floats, booleans, and characters implement `Copy`, so assignment copies the value instead of moving it, and both variables remain valid.

```rust
let x = 5;
let y = x; // copied, not moved
println!("{}, {}", x, y); // both valid
```

Passing a value to a function, and returning a value from a function, follow the same move rules as assignment.

## 5. Borrowing and References

Moving ownership into every function that needs to read a value is often impractical. Borrowing solves this: a reference grants access without transferring ownership.

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}

fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);
    println!("{} has length {}", s1, len); // s1 is still valid
}
```

References are immutable by default, matching the immutability-by-default rule for variables. Mutating through a reference requires an explicit mutable reference, `&mut T`, and the underlying variable must also be declared `mut`.

```rust
fn change(s: &mut String) {
    s.push_str(", world");
}

let mut s = String::from("hello");
change(&mut s);
```

### The core borrowing rule

Within a given scope, a value may have any number of immutable references, or exactly one mutable reference, but never both at the same time. The compiler enforces this at compile time.

```rust
let mut s = String::from("hello");
let r1 = &mut s;
let r2 = &mut s; // compile error: cannot borrow as mutable more than once at a time
```

This rule exists to prevent data races. If two references could write to the same memory simultaneously, or one could write while another reads, the result would be unpredictable. Rust rejects the possibility entirely at compile time rather than detecting it at runtime.

Rust's compiler tracks a reference's actual last use rather than its lexical scope (a feature known as non-lexical lifetimes), so a reference that is no longer used does not block a new borrow, even if it is technically still in scope.

### Dangling references are impossible

```rust
fn dangle() -> &String {
    let s = String::from("hello");
    &s
} // s is dropped here, but a reference to it was returned
```

This does not compile. The compiler recognizes that `s` is dropped at the end of the function and refuses to return a reference to memory that will no longer exist. The fix is to return ownership rather than a reference.

## 6. Lifetimes

Lifetimes are a compile-time-only concept. They add no runtime cost and change nothing about how memory is freed; they exist purely to let the compiler verify that a reference never outlives the data it points to.

In most cases, the compiler infers lifetimes automatically through a set of rules called lifetime elision. An explicit annotation becomes necessary only when there is genuine ambiguity, typically when a function takes multiple reference parameters and returns a reference.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

The annotation `'a` does not mean `x` and `y` must have identical lifetimes. It means the returned reference is guaranteed valid only as long as both `x` and `y` are valid, specifically as long as the shorter-lived of the two remains valid. This lets the compiler catch cases where the returned reference would otherwise outlive its source.

```rust
let string1 = String::from("long string is long");
let result;
{
    let string2 = String::from("xyz");
    result = longest(string1.as_str(), string2.as_str());
} // string2 is dropped here
println!("{}", result); // compile error: string2 does not live long enough
```

Structs that hold references also require lifetime annotations, expressing that an instance of the struct cannot outlive the data it references.

```rust
struct Excerpt<'a> {
    part: &'a str,
}
```

The special lifetime `'static` indicates a reference valid for the entire duration of the program, typically used for string literals compiled directly into the binary. It should not be used casually to silence a lifetime error, since doing so usually masks a design problem rather than solving it.

## 7. Structs

A struct groups related data into a custom type, similar to a class without inherited methods.

```rust
struct User {
    username: String,
    email: String,
    active: bool,
    sign_in_count: u64,
}
```

Struct instances follow the same immutability-by-default rule as variables. Mutability applies to the whole instance; Rust does not support marking individual fields as mutable while others remain immutable.

```rust
let mut user1 = User { /* fields */ };
user1.email = String::from("new@example.com"); // requires mut on user1
```

### Ownership within structs

Struct fields follow the same ownership rules as any other value. Moving a non-`Copy` field out of a struct instance invalidates only that field; other fields, particularly `Copy` types, remain accessible. This is called a partial move.

```rust
let username = user1.username; // moves username out
println!("{}", user1.active); // still fine, active was not moved
println!("{}", user1.username); // compile error, username was moved
```

### Methods

Methods are defined in an `impl` block. A method taking `&self` borrows the instance immutably; `&mut self` borrows it mutably; an associated function with no `self` parameter behaves like a static method.

```rust
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn square(size: u32) -> Rectangle {
        Rectangle { width: size, height: size }
    }
}
```

## 8. Enums and the Option Type

Rust enums are more expressive than enums in most other languages: each variant can carry its own distinct data.

```rust
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}
```

The `match` control flow construct is exhaustive by design: every variant must be handled, or the code will not compile. This converts a common class of runtime bug, an unhandled case, into a compile-time error.

```rust
match msg {
    Message::Quit => println!("quit"),
    Message::Move { x, y } => println!("move to {}, {}", x, y),
    Message::Write(text) => println!("{}", text),
    Message::ChangeColor(r, g, b) => println!("{}, {}, {}", r, g, b),
}
```

### No null values

Rust has no null. In its place, the standard library defines the `Option<T>` enum:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

Any value that might or might not be present is typed as `Option<T>`. Because `match` is exhaustive, the compiler forces every caller to explicitly handle both the `Some` and `None` cases before using the value, eliminating an entire class of null-reference bugs at compile time rather than at runtime.

The `Result<T, E>` enum follows the same pattern for operations that can fail:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

Functions that can fail return `Result<T, E>` instead of throwing an exception. The caller is required to handle both the success and failure cases explicitly, which makes error paths visible in the function signature rather than hidden in documentation or discovered at runtime.

## 9. CPython Memory Management: Reference Counting and the GIL

Understanding CPython's own memory model is a prerequisite for writing safe FFI code, because Rust code that touches Python objects must respect CPython's rules, not just Rust's.

### Reference counting

CPython's primary memory management strategy is reference counting rather than a tracing garbage collector as the primary mechanism. Every object carries a hidden counter of how many references point to it.

```python
a = [1, 2, 3]   # refcount = 1
b = a           # refcount = 2
del a           # refcount = 1
del b           # refcount = 0, object freed immediately
```

When the counter reaches zero, the object is deallocated immediately and deterministically. A separate generational garbage collector exists specifically to catch reference cycles, such as two objects referencing each other, that reference counting alone cannot free.

### The Global Interpreter Lock

This counter is not thread-safe by itself. If two threads increment or decrement it concurrently without coordination, the count can become corrupted, causing a premature free or a memory leak. CPython's solution is the Global Interpreter Lock, or GIL: only one thread may execute Python bytecode, and by extension touch Python objects, at any given time.

This is why multithreading in pure Python does not speed up CPU-bound work on a standard build. Threads gain real concurrency only around I/O waits, where the lock is released automatically while a thread blocks on a network call or file read. Note that this is a description of the traditional, GIL-enabled CPython build. Recent CPython and PyO3 versions also support an experimental free-threaded build (PEP 703), which removes the global lock entirely and relies on more granular synchronization instead. The GIL-centric model described here is still the one almost every production deployment runs today, but it is no longer a universal statement about all CPython builds.

## 10. PyO3: Bridging Rust and Python

PyO3 wraps CPython's C API in safe, ergonomic Rust, so that ordinary Rust functions can be exposed directly to Python. As of PyO3 0.26 and later, several core APIs were renamed to reflect the free-threaded build: `Python::with_gil` became `Python::attach`, and `Python::allow_threads` became `Python::detach`. The old names still work in current versions as deprecated aliases. This guide uses the current names.

```rust
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;

#[pyfunction]
fn add(a: i64, b: i64) -> i64 {
    a + b
}

#[pymodule]
fn my_rust_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add, m)?)?;
    Ok(())
}
```

```python
import my_rust_module
result = my_rust_module.add(5, 6)
```

When Python calls into a `#[pyfunction]`, PyO3 converts arguments from Python types into Rust types, and converts the return value back into a Python object. Current PyO3 versions perform this conversion through the `FromPyObject` trait for input and the `IntoPyObject` trait for output; the older `IntoPy` and `ToPyObject` traits from earlier PyO3 versions are deprecated in favor of `IntoPyObject`.

## 11. Extraction Versus Reference: The Safety Boundary

This is the central concept for writing correct PyO3 code and for understanding what kind of data may safely be used once the GIL is released.

### Extraction

When a function parameter is an owned Rust type such as `String`, `Vec<T>`, `HashMap<K, V>`, or a primitive, PyO3 copies the underlying data out of the Python object into a brand new, independently owned Rust value.

```rust
#[pyfunction]
fn process(text: String) -> usize {
    // 'text' is now fully Rust-owned, copied out of the Python str
    text.len()
}
```

After extraction, the resulting Rust value has no remaining connection to the original Python object. It is governed entirely by Rust's own ownership and drop rules, described in section 4, and can be used freely in a detached section with no further coordination required.

### Owned handles versus attached references

This distinction is more precise than a simple "owned data is safe, Python data is not" rule, and it is worth stating carefully because it is easy to get wrong.

`Py<T>` (also written as the alias `PyObject` for `Py<PyAny>`) is an owned handle to a Python object that is not tied to any particular attached thread state. It manages the object's reference count through Rust's Drop mechanism, the same way described in the paragraph above, and it may be moved into a detached closure (a `Python::detach` closure, formerly called `allow_threads`) without that by itself being undefined behavior.

```rust
#[pyfunction]
fn store_ref(obj: Py<PyAny>) {
    // 'obj' is an owned handle; PyO3 manages its refcount via Drop
} // when 'obj' is dropped, the refcount is decremented
```

What a `Py<T>` handle cannot do inside a detached section is access the underlying Python object's data or call Python methods on it, because doing that requires an attached Python thread state. To do that work, the thread must reattach first, typically with `Python::attach`, and only then dereference the handle.

`Bound<'py, T>` and the `Python<'py>` token itself are different: they are tied to a specific attached thread state through the `'py` lifetime, and must not be carried into a detached section at all. The compiler generally prevents this at the type level, since these types are not `Ungil` and PyO3's `detach` requires its closure and return value to be `Ungil`.

### Decision table

| Rust type | What it represents | Usable inside a detached (`Python::detach`) closure? |
|---|---|---|
| `i64`, `f64`, `bool` | Copied by value | Yes |
| `String`, `Vec<T>`, `HashMap<K, V>` | Extracted, independently owned | Yes |
| `Py<T>` (including `PyObject`) | Owned handle, refcount managed by Drop | May be carried in, but reattaching is required to touch the Python object itself |
| `Bound<'py, T>` | Reference tied to an attached thread state | No, must not cross into a detached section |
| `Python<'py>` (the GIL token) | Proof of an attached thread state | No, tokens cannot be shared across threads |

The practical rule for a batch accelerator: extract into owned Rust types before releasing the GIL whenever possible, since that avoids reattachment overhead entirely and gives the cleanest parallel section. `Py<T>` handles crossing into Rayon workers are a legitimate pattern when the workers occasionally need to touch the original Python object, but each worker must reattach for that specific access, and on a traditional GIL-enabled build repeated reattachment across many workers can serialize that portion of the work. Extraction is usually still the faster design when it is possible.

## 12. Rayon and Safe Parallelism

Rayon is covered in full depth, including its work-stealing scheduler and a complete list of situations where it should not be used, in the companion article linked at the top of this guide. The summary relevant to PyO3 integration follows.

Once data has been extracted into owned Rust types, the GIL can be released for the duration of a computation using `Python::detach`, allowing genuine multi-core execution.

```rust
#[pyfunction]
fn heavy_computation(py: Python) -> i64 {
    let data: Vec<i64> = vec![1, 2, 3, 4, 5];
    py.detach(|| {
        data.iter().sum() // safe: pure Rust-owned data, no attached Python state touched
    })
}
```

Rayon's parallel iterators, `par_iter()` and `par_iter_mut()`, do not require a mutex around each element because `par_iter()` hands out only immutable references and `par_iter_mut()` guarantees each thread a distinct, non-overlapping slice, so the borrow checker rules out overlapping mutable access at compile time. This does not mean Rayon runs without any synchronization at all; its work-stealing scheduler still coordinates worker queues, sleeping and waking threads, and task injection internally. What the borrow checker removes is the need for the developer to add locking around the data itself.

```rust
use rayon::prelude::*;

data.par_iter().map(|x| x * x).collect::<Vec<i64>>()
```

For an indexed source such as a `Vec` or slice, an order-preserving consumer like `collect::<Vec<_>>()` reconstructs the results in the original order even though individual elements were computed concurrently. This is not a general guarantee across every Rayon combinator; some operations, such as `par_bridge()`, explicitly do not preserve the source order.

`Python::detach` does not verify at compile time that its closure avoids touching attached Python state; that guarantee is provided by the `Ungil` trait bound on the closure and its return type, which is a real but imperfect mechanism, since it relies on `Send` in a way that does not catch every case. Carrying a `Bound<'py, T>` or the `Python<'py>` token itself into the closure will not compile. Carrying a `Py<T>` handle in and then reattaching inside a Rayon worker to touch the underlying object is a documented, supported pattern, not undefined behavior, though it is usually the slower option compared with extracting to owned data up front.

## 13. The Complete Production Pattern

```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn process_batch(py: Python, data: Vec<i64>) -> Vec<i64> {
    py.detach(|| {
        data.par_iter()
            .map(|&x| expensive_transform(x))
            .collect()
    })
}

fn expensive_transform(x: i64) -> i64 {
    x * x
}
```

The sequence is: extract while attached, detach from the interpreter, compute in parallel on owned data with Rayon, then reattach to convert the result back into a Python object. This single pattern removes both of Python's core limitations for CPU-bound work on a traditional build, the single-thread restriction of the GIL and the interpreter's per-element overhead, while relying on Rust's type system for most of the safety guarantees.

This pattern is appropriate specifically for CPU-bound hot paths. For I/O-bound code, such as connection handling or retry logic, extraction and parallelism provide little to no benefit, since the bottleneck is waiting rather than computing; an async runtime is usually the better fit there, though even that is workload-dependent rather than an absolute rule (see the companion Rayon article for the I/O-bound discussion in more detail).

## 14. Common Mistakes

- Assuming any `Py<T>` handle in a detached closure is automatically unsafe. It is not; what is unsafe is dereferencing it or calling into Python without first reattaching.
- Using the deprecated `allow_threads` / `with_gil` names in new code instead of `detach` / `attach`.
- Porting an I/O-bound function expecting a performance gain from Rust or Rayon.
- Extracting data element by element in a loop instead of extracting an entire batch once.
- Skipping black-box tests against the existing Python behavior before converting a function.
- Reaching for Rayon before profiling to confirm the target function is actually the bottleneck.
- Assuming Rayon's parallel iterators always preserve order; check the specific combinator being used.

## 15. Conclusion

Rust's ownership and borrowing rules, covered in sections 4 through 6, are not an isolated language feature. They are the same rules that make PyO3's extraction-versus-reference boundary safe, and the same rules that make Rayon's parallel iterators safe without runtime locks. Understanding ownership first makes every subsequent concept in this guide, from lifetimes to GIL safety to parallel iteration, a direct extension of the same small set of ideas rather than a new set of rules to memorize independently.

## Related Reading

[Rayon in Rust: How Threading Works and When You Should Never Use It as an Accelerator](https://your-blog-domain.example.com/rayon-threading-guide)

Official documentation: [The Rust Programming Language book](https://doc.rust-lang.org/book/), [the PyO3 user guide](https://pyo3.rs), [the Rayon documentation](https://docs.rs/rayon).
