# Asynchronous Programming with Tokio

Tokio is the industry-standard asynchronous runtime for building fast, reliable, and scalable network and I/O applications in Rust.

---

## 1. Core Tokio Architecture

- **Multi-threaded Work-Stealing Scheduler**: Worker threads run cooperative tasks.
- **Epoll / Kqueue Reactor**: Non-blocking network and timer events.
- **Futures & Polling**: Rust futures are pull-based and lazy; they do nothing until `.await`ed or spawned onto a runtime.

---

## 2. Spawning Tasks and Cooperative Scheduling

```rust
use tokio::task;

// Spawn an asynchronous background task
let handle = task::spawn(async move {
    fetch_metrics().await
});

let metrics = handle.await?;
```

### The Cardinal Rule: Never Block the Reactor
If a task runs CPU-heavy code or synchronous file I/O on an async worker thread, it starves other tasks scheduled on that thread:

```rust
// WRONG: blocks the async worker thread
let res = std::fs::read_to_string("large_file.txt")?;

// RIGHT: offload blocking operations to dedicated blocking threadpool
let content = tokio::task::spawn_blocking(|| {
    std::fs::read_to_string("large_file.txt")
}).await??;
```

---

## 3. Multiplexing with `tokio::select!`

`tokio::select!` waits on multiple asynchronous branches simultaneously and executes the handler for whichever future completes first:

```rust
use tokio::sync::mpsc;
use tokio::time::{self, Duration};

async fn run_worker(mut rx: mpsc::Receiver<Command>) {
    let mut interval = time::interval(Duration::from_secs(30));

    loop {
        tokio::select! {
            Some(cmd) = rx.recv() => {
                handle_command(cmd).await;
            }
            _ = interval.tick() => {
                send_heartbeat().await;
            }
        }
    }
}
```

### Cancellation Safety
When a branch in `tokio::select!` completes, other branches that were waiting are dropped immediately. Ensure that dropping a future does not leave your system in an inconsistent state. Operations like `mpsc::Receiver::recv()` are cancellation-safe; writing to a socket across multiple chunks may not be unless buffered.

