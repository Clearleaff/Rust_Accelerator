# Django-Specific Guardrails (delta on shared security guardrails)

- Do not log raw employee, HR, attendance, payroll, or biometric data — this is
  the concrete instance of the shared "no sensitive domain data in logs" rule.
- Treat leave-balance, payroll, and attendance calculations as canonical in
  their current Python form unless the user explicitly asks to fix a bug —
  Rust must match existing (even quirky) behavior, not "correct" it silently.
- Do not bypass Django signals that fire around save/update (e.g. audit-log
  signals, notification signals) by moving the calculation into Rust — the
  wrapper still triggers them exactly where the original code did.
- Document any new build-tool requirement (Rust toolchain, maturin) only in
  the deployment files that actually need it for building wheels; runtime
  images should install the pre-built wheel, not the whole toolchain.
