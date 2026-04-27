# ADR 0003: Conda for Environments, pip + pyproject.toml for Dependencies

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

Python projects must address two related but separable concerns:

1. **Environment management** — creating isolated Python installations so different projects' dependency sets do not collide.
2. **Dependency management** — declaring, resolving, locking, and installing the packages a project requires.

Several tools combine these concerns differently:

| Tool | Environment management | Dependency management |
|---|---|---|
| `conda` (Anaconda) | Yes | Yes (via `conda install` or `environment.yml`) |
| `venv` + `pip` | Yes (venv) | Yes (pip; declarative via `pyproject.toml`) |
| `poetry` | Yes (creates venvs) | Yes (full: declare, resolve, lock) |
| `uv` | Yes | Yes (very fast; full feature set) |

The project owner already uses Anaconda and is comfortable with `conda activate` / `conda create` workflows. The architecture document specifies a future AWS Lambda deployment, where the runtime is a standard Python interpreter consuming a pip-installable artifact — Conda is not used in Lambda packaging.

---

## Decision

Use **conda for environment management** and **pip + `pyproject.toml` for dependency management**, in combination:

1. `conda create -n ta-scanner python=3.12` creates the isolated Python environment.
2. `conda activate ta-scanner` enters the environment.
3. `pip install -e ".[dev]"` reads `pyproject.toml` and installs runtime + development dependencies.

Dependencies are declared exclusively in `pyproject.toml`. No `environment.yml`, no `requirements.txt`.

---

## Alternatives Considered

### Alternative A: Conda for everything (`environment.yml` + `conda install`)

Use Conda for both environment and dependency management, declaring all packages in `environment.yml`.

**Rejected because:**
- Creates a coupling between the project's dependency declaration format and the Conda toolchain. AWS Lambda does not consume `environment.yml`; the AWS phase would require translating to a pip-compatible format anyway.
- `pyproject.toml` is the universally portable format. Every Python deployment target understands it.
- Conda's package availability for FastAPI-ecosystem libraries (e.g., specific yfinance versions) is sometimes lagging or absent compared to PyPI.

### Alternative B: `venv` + `pip` (drop Conda)

Use Python's built-in `venv` module instead of Conda for environments.

**Rejected because:**
- The project owner is already proficient with Conda. Switching tools mid-project for no functional gain creates friction.
- Conda environments work cleanly with pip-installed packages; there is no compatibility issue forcing a switch.

### Alternative C: Poetry

Adopt Poetry as a unified environment + dependency tool.

**Rejected because:**
- Adds a new tool to learn, replacing one already in use (Conda).
- Poetry's lockfile and resolver are excellent but solve a problem (reproducibility across many developer machines) that does not apply to a single-developer project.
- Poetry's `pyproject.toml` extensions are slightly non-standard, which would create friction if the project ever moves to a different toolchain.

### Alternative D: uv

Adopt `uv` as a unified environment + dependency tool.

**Rejected for now, with explicit acknowledgment that this is a strong candidate to revisit later:**
- `uv` is genuinely excellent (10-100x faster than pip, single binary, full feature set including lockfiles).
- However, introducing a new tool mid-project is a distraction. The project owner does not currently have `uv` installed and the existing `conda + pip` workflow is sufficient.
- Worth revisiting in a future ADR if/when reproducibility requirements escalate (e.g., during AWS deployment phase).

---

## Consequences

### Positive

- Project owner uses an already-familiar tool (Conda) for environment management.
- `pyproject.toml` is the single, portable source of truth for dependencies. Works identically on a future fresh machine, on AWS Lambda, or in CI.
- Clean separation: Conda handles "which Python interpreter," pip handles "which packages." Each tool does what it is best at.
- No vendor lock-in to a specific dependency tool (Poetry, uv) that might be the wrong choice in three years.

### Negative

- Two tools instead of one (slight cognitive overhead).
- The combination is not the *most* modern setup; `uv` would be faster and conceptually simpler. Accepted trade-off for project-owner familiarity.

### Follow-up Required

- Revisit during AWS migration phase: at that point, the value of a true lockfile increases (multiple deployment environments must match exactly). Consider migrating to `uv` or adopting `pip-tools` / `pip-compile` for lockfile generation.

---

## Related

- ADR 0004 — dependency pinning strategy (related but separate concern)
- `pyproject.toml` — actual dependency declarations
