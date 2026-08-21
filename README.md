# Rust Accelerator Skills

> A community-maintained Codex skill collection for moving **measured, CPU-bound** hot paths from host applications into Rust safely.

This is a GitHub template repository for teams that want a consistent, evidence-led process for introducing Rust accelerators. It starts with a Django/Python plugin using PyO3 and maturin, plus framework-agnostic references for architecture, safety, testing, benchmarking, security, and maintainable boundaries.

Use this template to build a language-specific accelerator skill, adapt the existing Django skill to your conventions, or contribute another host-language plugin without duplicating the shared guidance.

## What this template protects

- Profile first: only migrate a path that materially dominates realistic end-to-end work.
- Preserve the host contract: callers, authorization, transactions, signals, data ownership, and rollback stay in the host application.
- Cross a narrow boundary: Rust receives plain owned data and returns plain data; framework objects never cross FFI.
- Ship safely: keep a feature-flagged host fallback, prove behavioral equivalence, and benchmark the complete path before enabling Rust by default.
- Keep Rust idiomatic: pure computations, explicit errors, no panics or `unsafe` without explicit approval.

## Repository layout

```text
skills/
  _shared/references/             # Cross-language engineering rules
  django-rust-accelerator/        # Django + PyO3/maturin plugin
    SKILL.md
    agents/openai.yaml
    references/                   # Django-only safety delta
docs/
  creating-a-plugin.md            # How to add another host stack
.github/                          # Community health files and templates
scripts/validate_skills.py        # Lightweight structural validation
```

## Use the template

1. Publish the repository and follow [docs/publishing-template.md](docs/publishing-template.md) to enable GitHub's template-repository setting.
2. Select **Use this template** on GitHub and create your repository.
3. Replace the placeholders in this README, [SECURITY.md](SECURITY.md), and `CODEOWNERS` if you add one.
4. Keep shared rules in `skills/_shared/references`; put framework-specific vocabulary and guardrails in a separate plugin directory.
5. Install or copy the relevant skill directory into your Codex skills location according to your local Codex setup.
6. Validate the repository before opening a pull request:

   ```bash
   python3 scripts/validate_skills.py
   ```

## Included skill: Django Rust Accelerator

Use `django-rust-accelerator` for slow Django views, serializers, services, reports, import/export paths, tasks, and other CPU-bound helpers. It defaults to an in-process PyO3 + maturin extension and makes the Django wrapper—not Rust—the owner of permissions, ORM access, transactions, and signals.

Read [the skill](skills/django-rust-accelerator/SKILL.md) and the shared references before using it. The companion [Rust and PyO3 guide](rust-pyo3-complete-guide%20%281%29.md) is a longer learning reference for engineers new to the boundary.

## Add a language plugin

See [docs/creating-a-plugin.md](docs/creating-a-plugin.md). New plugins extend the shared contract; they do not fork or weaken it. A good contribution usually contains:

- `SKILL.md` with framework vocabulary, binding decision, layout, and framework-only guardrails;
- `agents/openai.yaml` with a clear display name and starter prompt;
- `references/guardrails.md` containing only the framework-specific additions;
- links to every relevant file in `skills/_shared/references`.

## Contributing and support

Contributions are welcome—especially plugins for additional host stacks, clearer examples, and fixes backed by reproducible measurements. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the [Code of Conduct](CODE_OF_CONDUCT.md). For security concerns, use [SECURITY.md](SECURITY.md) rather than a public issue.

## License

This template intentionally does not choose a license for you. Add the license appropriate for your organization before publishing a derivative repository. If you maintain this upstream, replace this section with the selected license and a link to its file.
