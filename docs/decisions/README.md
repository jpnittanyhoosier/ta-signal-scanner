# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Technical Analysis Signal Scanner project. Each ADR captures a single significant decision: the context that prompted it, the options considered, the choice made, and the resulting consequences.

ADRs are **append-only**. When a decision changes, write a new ADR that supersedes the old one rather than editing the old one in place. The Git history of this directory is part of the project's reasoning record.

---

## Format

All ADRs follow this structure:

- **Status** — Proposed, Accepted, Superseded, Deprecated
- **Context** — what situation prompted the decision
- **Decision** — what was chosen
- **Alternatives Considered** — what else was on the table and why it was not selected
- **Consequences** — what becomes easier and what becomes harder as a result
- **Related** — links to related ADRs, architecture docs, or external references

---

## Index

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-repository-layout.md) | Top-level repository layout | Accepted | 2026-04-21 |
| [0002](0002-app-vs-src-layout.md) | Use `app/` rather than `src/` layout | Accepted | 2026-04-21 |
| [0003](0003-dependency-management-approach.md) | Conda for environments, pip + pyproject.toml for dependencies | Accepted | 2026-04-21 |
| [0004](0004-dependency-pinning-strategy.md) | Version-range pinning without lockfile (Option B) | Accepted | 2026-04-21 |
| [0005](0005-dev-tooling-selection.md) | Dev tools: pytest, ruff (lint + format), mypy | Accepted | 2026-04-21 |
| [0006](0006-mypy-lenient-configuration.md) | mypy configured in lenient mode initially | Accepted | 2026-04-21 |
| [0007](0007-defer-alembic-precommit.md) | Defer Alembic and pre-commit hooks to later phases | Accepted | 2026-04-21 |

---

## When to Write a New ADR

Write a new ADR when:

- A choice has multiple defensible options and you want to record *why* one was picked
- A decision will be hard to reverse later
- A future developer (including future-you) would otherwise need to ask "why was it done this way?"
- A decision overrides or modifies a prior ADR (write a new one with status "Supersedes ADR-NNNN")

You do not need an ADR for trivial choices, implementation details, or things that are easy to change later without consequence.
