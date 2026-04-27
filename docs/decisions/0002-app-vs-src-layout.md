# ADR 0002: Use `app/` Layout Rather Than `src/` Layout

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

Modern Python projects choose between three conventional layouts for their application code:

1. **Flat layout** — package directory at the repository root (e.g., `ta_signal_scanner/main.py`)
2. **`src/` layout** — package nested under a `src/` directory (e.g., `src/ta_signal_scanner/main.py`)
3. **`app/` layout** — application code in a directory named `app/` (e.g., `app/main.py`)

The `src/` layout is widely promoted by modern Python packaging guides (PyPA, hatchling docs) because it prevents a subtle bug class: when running tests from the repository root with the flat layout, Python may import the package directly from the source tree rather than from the installed location, masking packaging errors.

The `app/` layout is the dominant convention in the FastAPI / web-service ecosystem, where the project is a deployable application rather than a redistributable library.

This project must choose one.

---

## Decision

Use the **`app/` layout**. The application package lives at `app/` from the repository root.

---

## Alternatives Considered

### Alternative A: `src/ta_signal_scanner/` (src layout)

Place the application code under `src/ta_signal_scanner/`, following the modern PyPA recommendation.

**Rejected because:**
- The src layout's primary benefit (preventing accidental import from the source tree during testing) matters most for libraries published to PyPI, where the gap between development and consumer experience must be tightly controlled. This project is not a library.
- The src layout adds an extra directory level for every import path with no functional benefit for our deployment model.
- The accidental-import risk can be mitigated more cheaply by always invoking the application via `uvicorn app.main:app` rather than running modules directly from inside the package.

### Alternative B: `ta_signal_scanner/` (flat layout)

Place the application code at the repository root in a directory matching the project name.

**Rejected because:**
- Carries the accidental-import risk without offsetting benefit.
- Mixes application code with project metadata (README, pyproject.toml, etc.) at the same directory level, making the root harder to scan.
- The directory name `ta_signal_scanner` is project-specific and longer than `app`, adding noise to every relative path.

---

## Consequences

### Positive

- Matches FastAPI community convention; a developer familiar with FastAPI projects will navigate the structure intuitively.
- Imports are short: `from app.services.scoring import compute_posture` rather than `from src.ta_signal_scanner.services.scoring import compute_posture`.
- Clear visual separation at the repo root between application code (`app/`) and tests (`tests/`).
- The directory name `app/` accurately describes what lives there: a runnable application, not a library.

### Negative

- Diverges from the modern PyPA-recommended src layout. A Python packaging purist may flag this as non-idiomatic.
- The accidental-import risk exists in theory. Mitigated by always running the app through `uvicorn` and tests through `pytest`, never by `python app/main.py` from inside the directory.

### Follow-up Required

- None. The decision applies for the lifetime of the v1 codebase. AWS migration does not require a layout change.

---

## Related

- ADR 0001 — top-level repository layout
- `docs/repository-structure.md` — full tree
