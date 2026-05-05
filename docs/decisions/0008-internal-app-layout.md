# ADR 0008: Internal `app/` Layout — Layered by Architectural Ring

**Status:** Accepted
**Date:** 2026-05-04
**Deciders:** Project owner

---

## Context

ADR 0001 established the top-level repository layout. ADR 0002 settled on `app/` (rather than `src/ta_signal_scanner/`) as the application package directory. Both ADRs explicitly deferred the *internal* organization of `app/` to a later decision, to be made when the first models and routes were about to be written.

That moment has arrived. The first SQLAlchemy models, the first repository, a startup wiring file, and a `/health` route are about to be added. Each needs a home. Without an internal layout decision, every new file becomes its own micro-decision, and the cumulative result is unlikely to be coherent.

Three conventional approaches exist for organizing a Python web application's internal structure:

1. **Flat layout** — all modules at the top level of `app/`, named to indicate purpose (`models.py`, `scoring.py`, `yahoo_client.py`, etc.).
2. **Layered subdirectories** — one subdirectory per architectural ring, matching the hexagonal-lite design described in `architecture-design.md` §2 and §5.
3. **Feature-sliced** — one subdirectory per feature, each containing its own model + service + route + repository.

The architecture document was written assuming a layered structure. §4's diagram and §5's prose describe layers (web / service / data access / adapters / infrastructure), not features and not flat modules. A layout choice that diverges from layers would create permanent drift between the architecture document and the code.

A separate but related concern is **when** to physically create the layout's directories: all upfront (so the empty rings are visible from day one), or lazily (creating each subdirectory only when a file needs to live in it). Python community convention leans toward lazy creation; enterprise Java and Spring conventions lean toward upfront creation.

---

## Decision

### Part 1: Layout

Adopt **layered subdirectories**, with one subdirectory per architectural ring from the design document. The intended full structure is:

```
app/
├── __init__.py
├── main.py                       # FastAPI instance + startup wiring
├── web/                          # WEB LAYER (thin HTTP wrappers)
│   ├── __init__.py
│   ├── system.py                 # /health and other operational routes
│   ├── dashboard.py
│   ├── tickers.py
│   └── runs.py
├── services/                     # SERVICE LAYER (pure Python, no framework deps)
│   ├── __init__.py
│   ├── indicators.py
│   ├── scoring.py
│   └── orchestrator.py
├── dal/                          # DATA ACCESS LAYER
│   ├── __init__.py
│   ├── database.py               # Base, engine, session factory
│   ├── models.py                 # SQLAlchemy declarative models
│   ├── seed.py                   # leveraged_etf_defaults loader
│   └── *_repo.py                 # Repository classes (one file per repository)
├── adapters/                     # EXTERNAL INTEGRATIONS (anti-corruption boundary)
│   ├── __init__.py
│   └── yahoo_client.py
└── infra/                        # CROSS-CUTTING INFRASTRUCTURE
    ├── __init__.py
    └── scheduler.py              # APScheduler setup
```

The five subdirectory names map directly to the architecture diagram's subgraphs. Each subdirectory is one ring; each ring has its own dependency rules (per the design doc) and its own test posture (per ADR 0009).

### Part 2: Creation Policy

Create subdirectories **lazily** — only when a file needs to live in them. Empty placeholder directories are not created.

The intended full layout above is the *target*; the *current* layout at any moment reflects the work done to date. This ADR documents the intent so a reader can understand where future code will go without inspecting the tree. The current state of the tree at any moment is reflected in `docs/repository-structure.md`, which is updated as part of commit hygiene whenever structure changes.

---

## Alternatives Considered

### Alternative A: Flat layout

All modules at the top level of `app/`, no subdirectories.

**Rejected because:**
- The architectural rings would be invisible in the file tree. A new reader would need to read the architecture document and then mentally map each top-level file to a ring.
- The hexagonal-lite dependency rules (services do not import from web or dal; adapters are isolated) would have no structural enforcement. Any file could import any other file with no signal that the import crossed a ring boundary.
- The AWS migration story in `architecture-design.md` §9 promises "Service Layer — zero changes" and "FastAPI app wrapped in Mangum." Both promises are easier to keep when the relevant code is in a grep-able directory rather than scattered across flat modules.
- Scaling beyond v1 would force a restructure. When `indicators.py` outgrows itself, splitting it into `indicators/trend.py` and `indicators/momentum.py` creates a hybrid layout that is awkward without an enclosing `services/` directory.

### Alternative B: Feature-sliced (vertical slices)

Subdirectories named after features (e.g., `watchlist/`, `indicators/`, `runs/`), each containing its own model + service + route.

**Rejected because:**
- The project's "features" are tightly composed, not independent. Indicators feed scoring, scoring feeds orchestrator, orchestrator feeds dashboard. They do not have independent UIs or data flows that would benefit from per-feature directories.
- The anti-corruption layer (Yahoo adapter) has no natural home in a feature-sliced structure. It is consumed by the orchestrator, which spans multiple features. A `shared/` directory would have to absorb it and would tend to grow into a catch-all.
- The architecture document is layer-oriented. Choosing feature slices would require either rewriting the document or maintaining a permanent gap between documented architecture and physical structure.
- Feature slicing's primary benefit (multiple developers can own separate features) does not apply to a single-developer project.

### Alternative C: Layered with upfront directory creation

Same layout as the chosen Part 1, but with all five subdirectories and their `__init__.py` files created at the start of work even when empty.

**Rejected because:**
- Empty directories are not idiomatic in Python. Git does not track empty directories, requiring `.gitkeep` placeholder files that are themselves a smell.
- Python convention (and the project owner's learning materials) favor creating structure as it is needed. Adopting an upfront-creation policy would diverge from idiomatic Python practice for no functional benefit.
- The ADR documents the intended layout. A reader who wants to know where future code will go reads the ADR; the current state of the tree is reflected in `docs/repository-structure.md`. The tree itself reflects current state, not future plans.
- Trade-off accepted: a reader who *only* looks at the tree (and skips the ADR and the structure document) will not know what is coming. Mitigation: the ADR is short and findable; the architecture document references it; the structure document is updated as the tree evolves.

---

## Consequences

### Positive

- The architectural rings are visible in the file tree. The hexagonal-lite design becomes self-documenting.
- The dependency rules of the design are *grep-able*. A future linter rule (e.g., `flake8-tidy-imports` or a custom check) can enforce "nothing in `services/` imports from `web/` or `dal/`" mechanically.
- ADR 0009's ring-by-ring test posture maps cleanly: `tests/services/` holds service-ring tests, `tests/dal/` holds repository tests, `tests/web/` holds route smoke tests. Test location signals test posture.
- The AWS migration described in `architecture-design.md` §9 becomes localized. `web/` is re-wrapped with Mangum, `infra/scheduler.py` is deleted, `dal/database.py` swaps SQLite for Postgres. Other directories are unaffected.
- File naming inside each ring becomes simpler. `web/system.py` rather than `web_system.py`. `dal/models.py` rather than `dal_models.py`. The directory carries the ring identity; the filename only needs to carry the role.
- Lazy directory creation keeps the tree minimal. A reader sees only what currently exists, not what is planned.

### Negative

- Imports are slightly longer: `from app.services.scoring import compute_posture` instead of `from app.scoring import compute_posture`. Minor cost, paid every time an import is written.
- More `__init__.py` files exist over the project's lifetime (one per subdirectory). Each is small (typically empty) but adds to the file count.
- The tree at any single moment may be incomplete relative to the intended layout. A reader who relies only on the tree (skipping this ADR and the structure document) will not see the full picture. Mitigated by the ADR's existence and by `docs/repository-structure.md` reflecting current state.
- One judgment call per file: "is this `infra/` or `dal/`?" Most calls are obvious; a few are not. For example, the seed loader (`dal/seed.py`) could arguably live in `infra/` since it is startup-time operational code. The decision (`dal/`) reflects that it operates on data access concerns; if the boundary becomes painful, it can be revisited.

### Follow-up Required

- ADR 0009 (test coverage philosophy) will reference this layout for the ring-by-ring test posture. Expect `tests/` to mirror `app/`'s subdirectory structure.
- When the first cross-ring import that violates the dependency rule is *almost* written, consider adopting a linter rule to enforce the boundary. Not a v1 priority.
- If `services/` grows past one or two large modules, consider sub-grouping (e.g., `services/indicators/trend.py`, `services/indicators/momentum.py`). Decision deferred until the moment of pain.

---

## Related

- ADR 0001 — top-level repository layout (deferred this decision explicitly)
- ADR 0002 — `app/` directory naming (deferred this decision explicitly)
- ADR 0009 — test coverage philosophy (in progress; will reference this layout)
- `docs/architecture-design.md` §2, §4, §5 — the architectural rings this layout reflects
- `docs/repository-structure.md` — current state of the tree (updated as structure changes)
