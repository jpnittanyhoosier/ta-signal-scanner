# Repository Structure

**Project:** Technical Analysis Signal Scanner
**Status:** Target structure for v1 local implementation
**Date:** April 21, 2026

This document describes the target top-level layout of the `ta-signal-scanner` repository. It is a reference for initial repo setup and future onboarding. The internal structure of `app/` will be specified separately once the first models and routes are designed.

---

## Top-Level Tree

```
ta-signal-scanner/
├── app/                        # Application source code (Python package)
|   ├── __init__.py
├── tests/                      # Test suite, mirrors app/ structure
├── data/                       # Runtime data directory (SQLite db lives here)
│   └── .gitkeep                # Placeholder so the empty directory is tracked
├── scripts/                    # One-off utility scripts (db seed, debugging, etc.)
├── docs/                       # Project documentation
│   ├── architecture-design.md
│   ├── architecture-diagram.mmd
│   └── decisions/              # Architecture Decision Records (ADRs)
│       ├── README.md           # ADR index
│       ├── 0001-repository-layout.md
│       ├── 0002-app-vs-src-layout.md
│       ├── 0003-dependency-management-approach.md
│       ├── 0004-dependency-pinning-strategy.md
│       ├── 0005-dev-tooling-selection.md
│       ├── 0006-mypy-lenient-configuration.md
│       └── 0007-defer-alembic-precommit.md
├── .github/                    # GitHub-specific config (CI workflows, templates)
├── .gitignore                  # Files/directories Git should ignore
├── .python-version             # Python version pin (read by pyenv and similar tools)
├── .env.example                # Template for environment variables (real .env is gitignored)
├── pyproject.toml              # Project metadata, dependencies, tool configuration
├── README.md                   # Project overview and quickstart
└── LICENSE                     # MIT license (created on GitHub during repo setup)
```

---

## Folder and File Purposes

### `app/`
The runnable application. All FastAPI code, service layer, data access layer, and the Yahoo Finance adapter live here. Internal organization (web/service/dal/adapters subfolders) will be specified in a future thread once we design the first models and routes.

Contains a top-level `__init__.py` that marks the directory as a Python package. Required by mypy, IDEs, and pytest's import resolution. Future subdirectories under `app/` will each need their own `__init__.py` for the same reason.

### `tests/`
Pytest test suite. Mirrors the structure of `app/` so that finding the test for a given module is mechanical. Kept outside `app/` so test code is never accidentally shipped or imported by the running application.

### `data/`
Runtime directory for application state. The SQLite database file (`app.db`) will be created here at first run. The directory itself is committed via a `.gitkeep` placeholder file; the actual database file is gitignored.

### `scripts/`
Standalone utility scripts that are not part of the running web application: database initialization, seed-data loaders (e.g., the leveraged ETF defaults), backup helpers, ad-hoc diagnostic tools. Kept separate from `app/` to preserve a clean "this is the deployable application" boundary that matters for the future AWS Lambda packaging.

### `docs/`
All project documentation. The architecture design document and its diagram source are the source of truth for what the system does and how it is structured. The `decisions/` subfolder contains Architecture Decision Records (ADRs) — one file per significant decision, capturing context and rationale.

### `.github/`
Reserved for GitHub-specific configuration. Initially empty. Future contents may include:
- `.github/workflows/` — GitHub Actions CI pipelines (lint, test, type-check on PRs)
- `.github/ISSUE_TEMPLATE/` — issue templates
- `.github/pull_request_template.md` — PR template

Created at v1 even though empty so the slot exists when needed.

### `.gitignore`
Specifies files and directories that Git should never track. Critical to set up correctly before the first commit, because removing tracked files later requires history rewrites.

### `.python-version`
A one-line file containing `3.12`. Read by `pyenv` and other version-management tools. Documents the required Python version in a tool-readable form, complementing the `requires-python` declaration in `pyproject.toml`.

### `.env.example`
Template file showing which environment variables the application reads, with placeholder (non-secret) values. The real `.env` file (if needed) is gitignored. For v1 local, the application likely needs no environment variables; the file is created as a placeholder for the AWS phase, when secrets and config will be injected via environment.

### `pyproject.toml`
Single source of truth for: project metadata (name, version, description), runtime and development dependencies, and configuration for `pytest`, `ruff`, and `mypy`. Replaces the older pattern of separate `setup.py`, `requirements.txt`, `pytest.ini`, etc.

Includes an explicit `[tool.hatch.build.targets.wheel]` block declaring `packages = app/` This is required because hatchling's automatic package discovery does not find a directory whose name does not match the project name - and we deliberately chose `app/` over `ta_signal_scanner/` (see ADR 0002). The explicit configuration replaces the heuristic that would otherwise apply.

### `README.md`
First impression of the project for any reader (including future-you). Should contain: one-paragraph project description, prerequisites, quickstart (clone / install / run), and pointers to the `docs/` directory for deeper reading. Will be expanded as the project matures.

### `LICENSE`
MIT license. Already created on GitHub during initial repo setup.

---

## Files Deliberately Excluded From v1

These are common in larger Python projects but were considered and intentionally left out for v1. Reasoning is captured in the ADRs.

| Excluded | Reason | Future revisit point |
|---|---|---|
| `requirements.txt` | Superseded by `pyproject.toml`. Keeping both creates drift. | Never (do not add) |
| `Dockerfile` | Local v1 runs natively. Docker is part of the AWS phase. | AWS deployment phase |
| `Makefile` / `justfile` | Few enough commands that README quickstart suffices. | When command count grows past ~5 |
| `alembic/` (DB migrations) | Premature before the first schema exists. | Second schema change |
| `.pre-commit-config.yaml` | Local convenience tool; CI enforcement matters more. | When CI is added |
| `requirements.lock` / `requirements.txt` lockfile | Option C of pinning strategy; deferred per ADR 0004. | When AWS deployment requires reproducible builds |
| `conftest.py` (root) | Lives inside `tests/`, not at root. | N/A |
