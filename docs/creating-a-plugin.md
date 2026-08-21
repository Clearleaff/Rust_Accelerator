# Creating a host-language accelerator plugin

Each plugin adapts the same safe extraction workflow to a host stack. It should be small: shared engineering principles stay shared, while the plugin explains what those principles mean for one framework.

## Start from the contract

Read every document in `skills/_shared/references` before writing a plugin. A plugin must preserve these invariants:

1. A profiling result—not intuition—selects a CPU-bound candidate.
2. Host callers retain the same public behavior.
3. Host framework objects are converted to plain, owned data at the boundary.
4. Permissions, transactions, events, database ownership, and secrets remain in the host application.
5. The existing implementation stays as a feature-flagged fallback.
6. Differential tests, an exercised fallback, and an end-to-end benchmark gate rollout.

## Create the directory

```text
skills/<host>-rust-accelerator/
  SKILL.md
  agents/openai.yaml
  references/
    guardrails.md
```

The `SKILL.md` front matter needs a stable `name` and a precise `description` that says when to invoke it. Its body should provide:

- host vocabulary for the request/context, data layer, permissions, transactions, and feature flags;
- a default FFI or sidecar choice with the circumstances that justify another choice;
- an example layout that is conventional for the host ecosystem;
- a link to the shared references and to the local guardrail delta.

`agents/openai.yaml` provides the user-facing skill name, short description, and a useful initial prompt. Keep it aligned with the skill name and scope.

## Keep guardrails additive

`references/guardrails.md` may add framework-specific risks, such as middleware ordering, event-loop ownership, ORM behavior, deployment packaging, or domain constraints. It must never relax a rule in the shared security and safety references.

## Review checklist

- Does this describe an incremental extraction rather than a rewrite?
- Is the binding choice realistic for local development and deployment?
- Is host-owned state kept out of Rust?
- Are FFI errors mapped to host fallback rather than exposed to end users?
- Are timing and fallback metrics payload-free?
- Does `python3 scripts/validate_skills.py` pass?
