# ADR 0005: Development Tooling Selection

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

A Python project benefits from several categories of development-time tooling, each addressing a distinct concern:

- **Test runner** — executes test suites, reports pass/fail, supports fixtures and parameterization
- **Formatter** — enforces consistent code style automatically (whitespace, line breaks, quote style)
- **Linter** — catches likely bugs and style issues at edit time (unused imports, suspicious comparisons, etc.)
- **Type checker** — verifies that type annotations are internally consistent

Each tool has setup cost (configuration, learning curve) and runtime cost (CI time, friction on every commit). The decision is which subset to adopt for v1.

---

## Decision

Include the following dev tools, declared under `[project.optional-dependencies]` in the `dev` group of `pyproject.toml`:

| Tool | Role | Justification |
|---|---|---|
| `pytest` | Test runner | Industry standard; project owner already familiar |
| `pytest-asyncio` | Async test support | Required because FastAPI routes are async |
| `httpx` | HTTP client for testing | Required by FastAPI's recommended test client pattern |
| `ruff` | Linter + formatter | Single fast tool replacing 5+ legacy tools |
| `mypy` | Type checker | Lenient configuration (see ADR 0006) |

All five are installed via `pip install -e ".[dev]"`.

---

## Alternatives Considered

### For formatting: `black` instead of `ruff format`

`black` is the original opinionated Python formatter and remains widely used.

**Rejected because:** `ruff format` produces byte-identical output to `black` while running 10-100x faster and being part of the same tool that handles linting. Using `ruff` for both eliminates a dependency and a config surface.

### For linting: `flake8` + `isort` + `pylint` instead of `ruff`

The traditional stack: `flake8` for style, `isort` for import order, `pylint` for deeper analysis.

**Rejected because:** `ruff` reimplements the rule sets of all three (and more) in a single Rust binary that runs orders of magnitude faster. The traditional stack required three separate configurations and three separate runs. `ruff` has become the dominant Python linter for good reasons.

### For type checking: `pyright` instead of `mypy`

`pyright` (Microsoft) is the type checker that powers VS Code's Python language server. It is faster than `mypy` and has slightly different inference behavior.

**Rejected for explicit choice but accepted as background presence:**
- `pyright` will run automatically inside VS Code regardless of whether it is in `pyproject.toml`, providing real-time feedback during editing.
- `mypy` is what gets run in CI and what writes durable check results to logs / pre-commit / etc.
- The two tools largely agree; differences are at the margins.
- `mypy` is the more established standard and pairs better with the lenient configuration philosophy in ADR 0006.

### Skip type checking entirely

A defensible choice for small personal projects.

**Rejected because:** even a lenient `mypy` configuration catches a meaningful class of errors (typos, wrong argument types, return-type mismatches) at the layer boundaries that matter most in our hexagonal-lite design. The cost is small with the lenient config; the benefit at the service-layer-to-DAL and adapter-to-service interfaces is real.

### Add `pytest-cov` for coverage

Coverage reporting is useful but not essential for v1.

**Deferred:** can be added later with a one-line dependency change. Not worth the configuration overhead before the test suite has meaningful breadth.

---

## Consequences

### Positive

- The five tools cover all four categories (test, format, lint, type) with minimal overlap.
- `ruff` consolidates what would historically be 3-5 tool dependencies into one, reducing config surface and install time.
- Async test support is in place from day one, matching FastAPI's async-native architecture.
- Type checking is present but lenient (per ADR 0006), so it provides safety without becoming an obstacle.

### Negative

- New users of the project must install the `[dev]` extras to run tests or contribute. Standard practice; documented in README.
- Five additional dependencies in the dev environment (each with their own transitive deps) make `pip install -e ".[dev]"` slower than installing runtime deps alone. Acceptable; the install only happens once per environment setup.

### Follow-up Required

- Decide on `pytest-cov` (coverage) when the test suite is large enough for coverage metrics to matter.
- Decide on pre-commit hooks (`pre-commit` package) — see ADR 0007 for the deferral rationale.
- Decide on CI configuration (GitHub Actions running these tools on every PR) — out of scope for v1, will warrant its own ADR.

---

## Related

- ADR 0006 — mypy lenient configuration
- ADR 0007 — defer Alembic and pre-commit hooks
- `pyproject.toml` — actual tool configuration (`[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.mypy]`)
