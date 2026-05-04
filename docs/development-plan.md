# Development Plan

**Project:** Technical Analysis Signal Scanner
**Status:** Living document — revised as work proceeds
**Date:** April 30, 2026

---

## How to Use This Document

This plan is **milestone-based**, not phase-based. Each milestone describes a *state the project arrives at*; the route between milestones is flexible. The plan is **living** — milestones get added, reordered, split, or merged as work surfaces new information. Revisions are expected, not exceptional.

Three horizons of forward visibility:

- **Active Milestones (detailed)** — the next 2-3 milestones, specified at the template level. These guide near-term work.
- **Active Milestones (sketch)** — the rest of the v1 arc, title and one-line intent only. Committed to as scope, but not detailed because earlier milestones will reshape them.
- **Future Milestones** — post-v1, sketch only. Records forward-looking intent without commitment.

The mental model: detailed milestones are *this sprint*, sketch milestones are *this PI*, future milestones are *the product backlog*.

**Plan vs. ADRs.** The plan describes *what* happens at each milestone. ADRs describe *why* durable decisions were made. A milestone may spawn one or more ADRs; an ADR does not require a milestone. New ADRs are written as significant decisions arise during execution.

**Loaded at thread starts** alongside `architecture-design.md` to provide continuity across multi-thread work.

---

## Stated Principles

Cross-cutting principles that govern multiple milestones. Named so they can be referenced without re-derivation.

- **Adapter return types are domain types, not external types.** External integrations (yfinance today, AWS clients tomorrow) return *internal* data structures the domain owns, never raw responses from the external library. This is the **anti-corruption layer** pattern operating at full strength: when the external contract changes, the fix is localized to the adapter. Without this, the architecture document's §5.2 promise of localized breakage cannot be kept.

- **Test by ring, not by line count.** Service layer (pure functions) is tested rigorously per the ADR 0009 checklist. Adapters are tested by contract using fixtures, not by hitting live dependencies. Web routes are smoke-tested for wiring only — service logic is not re-tested through routes.

---

## Open Methodology Questions

Cross-cutting questions not yet resolved. When resolved, they either move into Stated Principles or become an ADR.

| # | Question | Status | Likely resolution |
|---|---|---|---|
| Q1 | Test coverage philosophy: what gets tested, how rigorously, when written? | Proposed answer agreed verbally; ADR pending | ADR 0009 in M1 |
| Q2 | Internal `app/` directory layout | Pending | ADR 0008 in M1 |
| Q3 | Internal data model design (dataclass vs. Pydantic, shape, location) | Pending | ADR 0010 in M2 |

---

## Active Milestones (Detailed)

### M1 — App skeleton runs end-to-end

**Goal:** A runnable FastAPI process with a health endpoint, the five SQLAlchemy models defined, and a test harness proven by passing tests at each architectural ring.

**Why now:** Everything downstream needs an importable `app/` package, a database to talk to, and a test runner that exercises real code. Without these, every later milestone is blocked.

**Scope:**
- Internal `app/` directory layout decided and implemented (web / services / dal / adapters / models, exact shape per ADR 0008)
- SQLAlchemy declarative base + models for all five tables from architecture §5.3 (`watchlist`, `price_history`, `ticker_thresholds`, `leveraged_etf_defaults`, `run_history`)
- DB session/engine setup with SQLite at `./data/app.db`
- `Base.metadata.create_all()` invoked at startup (no Alembic per ADR 0007)
- `app/main.py` with FastAPI instance and `/health` endpoint
- One test per ring: a model instantiation test, a repository smoke test (in-memory SQLite), a route test for `/health`
- `leveraged_etf_defaults` seed data loaded on first startup if table is empty

**Out of scope:**
- Any indicator, scoring, or Yahoo logic
- Any UI or templates
- Any scheduling
- Repository methods beyond what the smoke test needs

**Decisions this milestone forces:**
- ADR 0008 — internal `app/` layout
- ADR 0009 — test coverage philosophy (with the edge-case category checklist)
- Where seed data lives and how it loads (small enough to record in the plan, not warrant an ADR)

**Definition of done:**
- `uvicorn app.main:app` starts without error
- `GET /health` returns 200
- `app.db` exists with all five tables and seed data populated
- `pytest` runs green with at least one test per ring
- ADRs 0008 and 0009 committed

---

### M2 — Yahoo adapter fetches and persists daily bars

**Goal:** A single ticker's daily OHLC history can be fetched from Yahoo via the adapter and persisted to `price_history` via the repository, with the adapter returning internal domain types.

**Why now:** The adapter is the project's largest external risk (`yfinance` breaks periodically when Yahoo changes its HTML). Building it early means later milestones inherit a working data path; deferring it means indicator/scoring work uses fixtures and gets a rude integration surprise at the end. This is the **anti-corruption layer** pattern's first concrete application.

**Scope:**
- `YahooFinanceClient` with the interface declared in architecture §5.2
- Adapter returns internal domain types (e.g., `list[PriceBar]`), never raw `yfinance` DataFrames — per the Stated Principle above
- `PriceHistoryRepo` with insert/upsert and read-by-ticker methods (**repository pattern**)
- Idempotent persistence — re-fetching the same range produces no duplicate rows
- Adapter unit tests using recorded fixtures (no live Yahoo calls in the suite)
- One end-to-end manual verification (live fetch of one ticker, inspect `app.db`)

**Out of scope:**
- Iterating the watchlist (M5)
- Any indicator math (M3)
- Sophisticated error recovery beyond logging and propagating

**Decisions this milestone forces:**
- ADR 0010 — internal data model design (dataclass vs. Pydantic, field shape, module location). The shape chosen here sets a precedent that M3's `IndicatorSet` and downstream types will follow, so it warrants formal capture.
- Fixture recording approach — capture-once helper script vs. hand-crafted minimal CSVs. Probably a discussion, not an ADR.

**Definition of done:**
- A test or script invocation fetches one ticker's last 30 days and persists them
- Re-running the same fetch produces zero duplicate rows
- Adapter unit tests pass against fixtures with no network
- Adapter return type is an internal domain type, not a `yfinance` DataFrame
- ADR 0010 committed

---

### M3 — Indicators compute correctly from persisted data

**Goal:** All nine indicators from architecture §6 are implemented as pure functions, tested per the ADR 0009 checklist, and bundled into a structured indicator object per ticker.

**Why now:** Indicators are the highest-value, lowest-risk service-layer work. Pure functions, deterministic, easy to test, and they unblock M4 (scoring needs indicators as input). Doing them after the data path (M2) means we test against real-shaped data, not invented fixtures.

**Scope:**
- Functions for each of the nine indicators in §6: SMA-50, SMA-200, price-vs-SMA % distances, crossover state, RSI-14, HV-20 annualized, HV-20 trailing-year percentile, 52-week high/low, % distances from 52w extremes
- A structured `IndicatorSet` object bundling them per ticker (shape per ADR 0010 precedent)
- Each function tested per the applicable ADR 0009 categories
- Known-answer tests for the three with non-trivial math: SMA, RSI, HV
- A `compute_indicators(price_history) -> IndicatorSet` orchestrating function

**Out of scope:**
- Scoring logic (M4)
- Threshold comparison (M4)
- Persistence of indicator results — computed on demand from `price_history`, not stored

**Decisions this milestone forces:**
- Whether indicator functions live in one module or split by category (trend / momentum / volatility / range). Discussion-level, not ADR-level.

**Definition of done:**
- All nine indicators implemented as pure functions (no I/O, no global state)
- Each function has tests covering applicable ADR 0009 categories
- Known-answer tests pass for SMA, RSI, HV
- `compute_indicators` produces a populated `IndicatorSet` from a `PriceHistoryRepo` query result

---

## Active Milestones (Sketch)

The remaining v1 arc. Committed scope, intentionally undetailed because M1-M3 outcomes will reshape them.

- **M4 — Scoring produces postures from indicators and thresholds.** Scoring function implemented; `ThresholdsRepo` and `leveraged_etf_defaults` wired in; given an `IndicatorSet` and per-ticker thresholds, produces score and posture label.
- **M5 — Run orchestrator ties it together.** Iterates watchlist, fetches, computes, scores, persists run. Staleness check on startup. APScheduler wired in. **Density flag:** orchestrator + staleness + scheduler is arguably three milestones bundled into one because they're meaningless individually. Likely to split during execution if it grows beyond a single coherent unit of work.
- **M6 — Dashboard read path.** Jinja2 dashboard template, FastAPI route renders posture cards and indicator table from latest run. No charts, no interactivity. First moment the project feels real.
- **M7 — Ticker config write path.** Watchlist add/remove and threshold edit via UI. First mutating routes. Per-ticker overrides flow through to scoring.
- **M8 — Plotly charts on dashboard.** Price + SMA overlays, vanilla JS wiring to Plotly CDN. Dashboard now matches what architecture §5.1 describes.
- **M9 — Run history view.** Posture evolution per ticker over time. 18-month retention enforcement (nightly prune job). Staleness badge UI.
- **M10 — Polish and v1 close.** Error-handling pass, structured logging to stdout, README updates, deferred small items. Declares v1 complete.

---

## Future Milestones

Post-v1. Recorded for forward visibility; not committed scope.

- AWS migration prep — lockfile adoption (likely supersedes ADR 0004), Mangum wrapping, RDS-compatibility audit of repository code
- AWS deployment — Lambda + API Gateway + RDS Postgres + EventBridge + Cognito + Secrets Manager, per architecture §9
- Backtesting engine — preserved as an option by `price_history` indefinite retention
- Market-wide aggregate signals — distinct from per-ticker views; would require new portfolio/market view layer

---

## Completed Milestones

*(Append-only log. Milestones move here from Active when complete, with completion date.)*

- *(none yet — M1 in progress)*
