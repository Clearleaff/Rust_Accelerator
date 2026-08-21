# Publishing this as a GitHub template

After pushing this repository to GitHub:

1. Open the repository **Settings**.
2. In **General**, enable **Template repository**.
3. Add a short description and topics such as `codex`, `rust`, `pyo3`, `django`, `performance`, and `skills`.
4. Choose and commit a license before making the repository public.
5. Replace the `OWNER/REPOSITORY` placeholders in `.github/ISSUE_TEMPLATE/config.yml` and add a monitored private security-reporting channel in `SECURITY.md`, or enable GitHub private vulnerability reporting.
6. Protect the default branch and require the **Validate skills** workflow for pull requests.

GitHub's template status is repository configuration, so it cannot be enabled by a file committed to the repository. This document keeps the required publishing action visible to maintainers.
