# Contributing

Thank you for improving Rust Accelerator Skills. This repository is intentionally conservative: a plugin should make accelerators safer and more repeatable, not make a full rewrite look easier than it is.

## Before opening a pull request

1. Discuss substantial new plugins or changes to shared policy in an issue first.
2. Keep the change focused. Framework-specific content belongs in that plugin; rules shared by all host stacks belong in `skills/_shared/references`.
3. Preserve the core contract: profile first, use plain-data boundaries, retain a host fallback, and require equivalence testing plus end-to-end benchmarks.
4. Run the structural check:

   ```bash
   python3 scripts/validate_skills.py
   ```

5. Update the README and relevant references whenever behavior or the repository layout changes.

## Adding a plugin

Follow [docs/creating-a-plugin.md](docs/creating-a-plugin.md). Do not copy shared reference content into a plugin. Link to the shared source and add only host-specific terms, defaults, and guardrails.

## Writing guidance

- Write imperative, testable instructions rather than general advice.
- State assumptions and decision gates. Avoid claiming a speedup without a reproducible benchmark.
- Treat existing host behavior as canonical unless a change explicitly asks to change it.
- Never include secrets, personal data, production payloads, or customer-identifying benchmark data.
- Keep examples safe by default: no panics across FFI, no hidden concurrency, no framework object crossing the boundary.

## Pull request expectations

Explain the problem, the affected skill or reference, and how you validated the change. For a new host stack, include a small example of its FFI boundary and fallback shape. Maintainers may request changes where a proposal weakens security, rollback, observability, or behavioral-equivalence guarantees.
