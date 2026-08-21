---
name: django-rust-accelerator
description: Django/Python plugin for the Rust accelerator framework. Use when converting a slow Django view, serializer, service, payroll/reporting calculation, import/export, background task, or CPU-bound helper into Rust via PyO3/maturin. Loaded by rust-accelerator-core; can also be invoked directly if the host stack is already known to be Django.
---

# Django Rust Accelerator (plugin)

Always load `../_shared/references/*.md` first — this file only defines what
Django-specific terms mean and adds Django-only guardrails. It does not repeat
OOP/SOLID/Rust-safety content; see the shared files for that.

## Vocabulary for this host

- **"The ORM"** = Django's QuerySet/Model layer. Never pass a QuerySet or Model
  instance into Rust — resolve it to plain dicts/dataclasses in the wrapper
  first (`list(qs.values(...))` or `dataclasses.asdict(...)`).
- **"The request object"** = Django's `HttpRequest`/DRF `Request`. Never crosses
  the boundary.
- **"The permission layer"** = DRF permission classes / `@permission_required` /
  `@login_required`. These run in Django exactly as before; Rust never
  re-implements or bypasses them.
- **"The feature flag"** = a Django setting, conventionally
  `USE_RUST_ACCELERATORS` (or a per-feature variant), read via
  `django.conf.settings`.
- **"Signals/transactions"** = Django signals and `transaction.atomic()` blocks
  stay exactly where they are; the Rust call happens inside the same
  transaction boundary the original code had, not around it.

## Binding

Default to **PyO3 + maturin** (in-process extension) per
`../_shared/references/ffi-integration-patterns.md`. Only consider a sidecar
service if the workload is independently scalable or shared by non-Django
consumers — flag that as a bigger architectural decision and confirm with the
user first.

## Layout

```text
rust/django_accelerators/
  Cargo.toml
  pyproject.toml
  src/lib.rs
  src/<domain>.rs

<django_app>/
  accelerators.py
  tests/test_<domain>_accelerator.py
```

## Django-only guardrails

See `references/guardrails.md` in this folder for the delta on top of
`../_shared/references/security-and-privacy-guardrails.md` (HR/payroll/
attendance specifics).
