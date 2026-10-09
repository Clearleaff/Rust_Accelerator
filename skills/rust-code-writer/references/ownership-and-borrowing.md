# Ownership, Borrowing, and Lifetimes in Rust

This reference details the mechanics and patterns of Rust's core memory model.

## 1. Ownership Principles

1. Each value in Rust has an owner (a variable binding).
2. There can only be one owner at a time.
3. When the owner goes out of scope, the value is dropped and memory is immediately reclaimed (RAII).

### Moves vs Copies

- **Copy Types**: Types that reside entirely on the stack and implement `Copy` (e.g., `i32`, `f64`, `bool`, `char`, fixed-size arrays/tuples of `Copy` types). Assignment and function calls duplicate bits without invalidating the source.
- **Move Types**: Types that own heap allocations or system resources (`String`, `Vec<T>`, `Box<T>`, file handles). Assignment or passing by value transfers ownership. The previous binding is invalidated at compile time.

```rust
// Move example
let s1 = String::from("hello");
let s2 = s1; // s1 is moved and no longer accessible

// Copy example
let n1: u32 = 42;
let n2 = n1; // n1 is copied, both n1 and n2 remain valid
```

## 2. Borrowing Rules

Instead of transferring ownership, functions can borrow values using references:
- **Shared Reference (`&T`)**: Grants read-only access. You can have any number of shared references at the same time.
- **Exclusive / Mutable Reference (`&mut T`)**: Grants read and write access. You can have **only one** mutable reference to a piece of data at a time, and no simultaneous shared references.

```rust
let mut counter = 0;

let r1 = &counter;
let r2 = &counter;
// println!("{}", counter); // OK: multiple shared borrows

// let r3 = &mut counter; // COMPILE ERROR: cannot borrow as mutable while shared borrows exist
println!("{} and {}", r1, r2);

// Non-lexical lifetimes: r1 and r2 are no longer used here, so mutable borrow is allowed:
let r3 = &mut counter;
*r3 += 1;
```

### Preventing Dangling References

Rust guarantees that references will never outlive the data they point to:

```rust
// This will NOT compile:
// fn create_dangle() -> &String {
//     let s = String::from("local");
//     &s // s is dropped here!
// }

// Correct: return ownership
fn create_owned() -> String {
    let s = String::from("local");
    s
}
```

## 3. Lifetimes and Annotation Patterns

Lifetimes are compile-time parameters denoting the scope for which a reference is valid.

### Lifetime Elision Rules
The compiler infers lifetimes in 3 common scenarios:
1. Each elided lifetime in function arguments receives a distinct lifetime parameter.
2. If there is exactly one input lifetime parameter, that lifetime is assigned to all elided output lifetimes:
   ```rust
   fn first_word(s: &str) -> &str // compiler treats as fn first_word<'a>(s: &'a str) -> &'a str
   ```
3. If there are multiple input lifetime parameters, but one of them is `&self` or `&mut self`, the lifetime of `self` is assigned to all elided output lifetimes.

### Explicit Annotations

When returning a reference whose source is ambiguous among multiple arguments:

```rust
pub fn choose_longer<'a>(s1: &'a str, s2: &'a str) -> &'a str {
    if s1.len() >= s2.len() { s1 } else { s2 }
}
```

### Structs Holding References

```rust
pub struct Highlight<'a> {
    pub excerpt: &'a str,
    pub index: usize,
}
```
An instance of `Highlight<'a>` cannot outlive the string slice stored in `excerpt`.

## 4. Practical Anti-Patterns to Avoid

- **Fighting the Borrow Checker with `Rc<RefCell<T>>` Everywhere**: Do not use runtime borrow checking as an architectural band-aid for flawed data models. Prefer clear data ownership trees, indices, or passing state explicitly.
- **Uncontrolled Cloning in Tight Loops**:
  ```rust
  // Bad
  for item in items.iter() {
      process(item.clone());
  }

  // Good
  for item in items {
      process(item); // pass &Item or consume Item by value
  }
  ```
- **Overusing `'static`**: Avoid using `&'static str` or `'static` bounds unless you are working with string literals or spawning threads with detached lifetimes.

