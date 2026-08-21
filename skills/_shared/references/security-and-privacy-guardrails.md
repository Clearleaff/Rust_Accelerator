# Security & Privacy Guardrails (Language-Agnostic)

These are non-negotiable across every language plugin. Plugins may only ADD
framework-specific guardrails on top — never relax these.

## Data handling
- Do not log raw sensitive domain data: PII, payroll/compensation figures,
  health/biometric data, authentication tokens/secrets, or raw uploaded file
  contents. Log shapes/sizes/counts instead ("processed 412 records"), never
  values.
- Do not expose Rust stack traces or internal error strings to end users —
  translate to a generic host-language exception/error type at the wrapper.
- Check any uploaded/external file parsing for size limits and malformed or
  malicious input before it reaches Rust.

## Boundary discipline
- Do not pass live host objects across the boundary: no ORM/entity instances,
  no request/session objects, no database connections/handles, no lazy
  translation objects.
- Do not create a second, Rust-owned path to the database unless the user has
  explicitly approved that as a deliberate service-architecture decision.
- Do not bypass the host framework's permission checks, authorization
  middleware, audit logging, signals/events, or transaction boundaries by
  moving logic into Rust. If the extracted function used to run inside a
  transaction or after a permission check, the wrapper must still run inside
  that same transaction / after that same check.
- Keep migrations, schema/model definitions, and admin/console behavior in the
  host language — never in Rust.

## Rust-side safety (cross-reference)
See `rust-idioms-and-safety.md` for the code-level rules (no `unsafe`, no
`unwrap`/panics, explicit concurrency). Those rules exist partly for
correctness and partly for security: a panic or an out-of-bounds access in a
native extension can take down the whole host process, which is a much bigger
blast radius than a caught exception in the host language.

## Secrets
Keep all secrets/credentials in the host language's existing settings/env
handling. Never hardcode a secret in Rust source, and never pass a secret
value across the boundary unless the accelerated function genuinely needs to
authenticate to something itself (rare — flag this to the user if it comes up).
