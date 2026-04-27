# ADR 0001: Top-Level Repository Layout

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

The project requires a top-level repository structure before any application code is written. The structure must:

- Support the v1 local deployment (FastAPI + SQLite + APScheduler) defined in `architecture-design.md`
- Support a future migration to AWS (Lambda + RDS + EventBridge) without significant restructuring
- Match conventions familiar to Python web developers, so external collaborators (or future-self after time away) can navigate it without surprise
- Avoid premature complexity: we do not want to carry tooling overhead for capabilities we are not yet using

The decision is the set of top-level folders and files only. The internal organization of `app/` is deferred to a later ADR once the first models and routes are designed.

---

## Decision

Adopt the following top-level layout:

```
ta-signal-scanner/
├── app/
├── tests/
├── data/
├── scripts/
├── docs/
├── .github/
├── .gitignore
├── .python-version
├── .env.example
├── pyproject.toml
├── README.md
└── LICENSE
```

Each entry has a single, well-defined purpose documented in `repository-structure.md`.

---

## Alternatives Considered

### Alternative A: Minimal layout (`app/`, `tests/`, `pyproject.toml`, `README.md` only)

Defer creation of `data/`, `scripts/`, `docs/`, `.github/`, `.env.example`, and `.python-version` until they are actually needed.

**Rejected because:** Several of these directories cost nothing to create empty (or with placeholder content) and prevent the friction of adding them later mid-stride. `docs/` in particular needs to exist immediately to house the architecture design document. Creating empty slots now is cheap insurance.

### Alternative B: Heavyweight layout (add `Makefile`, `Dockerfile`, `alembic/`, `.pre-commit-config.yaml`)

Front-load the tooling that a mature project would have.

**Rejected because:** Each of these adds cognitive overhead and a maintenance burden in exchange for capability we do not yet need. `Dockerfile` belongs to the AWS phase. `alembic/` is premature before any schema exists (see ADR 0007). `Makefile` is unnecessary while the command count is small. `.pre-commit-config.yaml` is convenience tooling that is genuinely useful but introduces a separate concept; deferring keeps the v1 surface area smaller.

### Alternative C: Co-locate `tests/` inside `app/` (i.e., `app/tests/`)

Some Python projects keep tests next to the modules they test.

**Rejected because:** Co-located tests get accidentally packaged and shipped with the application, which matters when the AWS phase requires lean Lambda deployment artifacts. Keeping `tests/` at the top level cleanly separates testable artifact from tested artifact.

---

## Consequences

### Positive

- The architecture design document has an immediate home in `docs/`.
- The `data/` directory exists from clone-time, so first-run does not require directory creation in application code.
- Empty `.github/` and `scripts/` slots reduce friction when those capabilities are added later.
- Clear separation between application code (`app/`), tests (`tests/`), runtime data (`data/`), utility scripts (`scripts/`), and documentation (`docs/`) supports the hexagonal-lite discipline established in the architecture document.

### Negative

- A few folders (`.github/`, `scripts/`) start empty, which can look like noise to a new reader. Mitigated by the explanatory README and `repository-structure.md`.
- A `.gitkeep` placeholder is needed in `data/` to commit the empty directory, which is a minor idiom that needs explaining once.

### Follow-up Required

- Internal layout of `app/` to be specified in a future ADR.
- Internal layout of `tests/` follows from `app/`, no separate decision needed.

---

## Related

- `docs/architecture-design.md` — full system design
- `docs/repository-structure.md` — annotated tree
- ADR 0002 — choice of `app/` over `src/ta_signal_scanner/` for the application package directory
