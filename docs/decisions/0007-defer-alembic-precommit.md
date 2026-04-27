# ADR 0007: Defer Alembic and pre-commit Hooks to Later Phases

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

Two tools commonly found in mature Python projects were considered for inclusion in v1 and explicitly deferred:

1. **Alembic** — a database schema migration tool. Tracks intentional schema changes as versioned migration scripts, allowing the live database to be evolved while preserving data.

2. **pre-commit** (the framework) — a tool that runs configured checks (linters, formatters, etc.) automatically before each Git commit, blocking commits that fail.

Both tools are professional standards. Both add real value when used appropriately. Both also add concept-load and configuration surface that may not pay off at v1 scale.

This ADR captures the rationale for deferring each and the conditions that should trigger reconsideration.

---

## Decision

**Defer both Alembic and pre-commit for v1.** Neither appears in `pyproject.toml`. Neither has configuration files committed.

Plan to revisit:
- **Alembic** at the second schema change (after the first models exist and have stabilized)
- **pre-commit** when a CI pipeline is introduced, so the same checks can run in both places

---

## Alternatives Considered

### Alternative A: Include Alembic from v1

Set up Alembic from the start, generate an initial migration containing the first schema, and use migrations for all schema changes thereafter.

**Rejected because:**
- Before any models exist, there is nothing to migrate from. The first Alembic migration would simply be "create all tables," which `Base.metadata.create_all()` accomplishes in one line of code with no ceremony.
- Alembic's value compounds with the *number of schema changes* over time. The first change has near-zero migration value; the second through nth have high value.
- Setting up Alembic early commits the project to a workflow (always generate migration, always review, always apply) before the developer has felt the pain it solves. This often results in skipped or sloppy migrations, defeating the purpose.
- Adding Alembic later is approximately a 30-minute task that does not require changing existing code — only adding the migration framework and generating an initial baseline migration.

### Alternative B: Include pre-commit from v1

Set up `.pre-commit-config.yaml` running `ruff check`, `ruff format --check`, and basic file-hygiene checks.

**Rejected because:**
- Pre-commit hooks are *local convenience*, not enforcement. A developer can bypass them with `git commit --no-verify` or by simply not running `pre-commit install`. Real enforcement happens in CI.
- For a single-developer project with no CI, pre-commit is the only check — but it is also the most easily bypassed check. The discipline to not bypass is the actual quality control, not the tool.
- Adding pre-commit alone (without CI) creates a false sense of safety: "the hook will catch it" leads to checking less carefully manually, but the hook can be bypassed in moments of haste.
- The mature pattern is **pre-commit locally + the same checks in CI**. Adding pre-commit before CI is putting on one shoe.

### Alternative C: Include both from v1

Adopt the full mature-project tooling stack at v1.

**Rejected because:** the combined cognitive overhead of learning both tools while also writing the application is meaningful. v1's primary risk is "developer loses momentum and the project stalls," not "developer ships a buggy v1." Tooling that increases friction relative to its current benefit is anti-helpful at this phase.

---

## Triggering Conditions for Reconsideration

### Adopt Alembic when:

- The first schema change after initial deployment is needed (i.e., the `app.db` file contains data the developer wants to preserve through the change)
- A second developer begins contributing and needs reproducible schema setup
- The AWS migration phase begins (RDS Postgres requires explicit migration management; cannot rely on `create_all()` against a live database)

### Adopt pre-commit when:

- A CI pipeline (GitHub Actions running ruff, pytest, mypy) is configured. At that point, pre-commit becomes the local mirror of the CI checks, providing fast feedback before push.
- The developer notices they are repeatedly catching issues in CI that pre-commit would have caught locally.

---

## Consequences

### Positive

- v1 has a smaller surface area to learn, configure, and maintain.
- Schema changes during v1 development can be made by editing models and recreating the database file (acceptable while no data is precious).
- Code quality during v1 is enforced by manually running `ruff check`, `ruff format`, and `pytest` — same tools that would run in pre-commit, just without automation.

### Negative

- Manual discipline is required to run linters/formatters before commit. Some commits will land with formatting issues. Mitigated by VS Code's "format on save" feature, which can be enabled in editor settings.
- The first schema change with real data to preserve will require some Alembic learning at that moment, rather than having the framework already in place. Estimated cost: 30-60 minutes when the time comes.

### Follow-up Required

- Document the trigger conditions in a visible place so they are not forgotten.
- When CI is added, write a follow-up ADR adopting pre-commit and pinning tool versions identically between local and CI.
- When the first significant schema change arrives, write a follow-up ADR adopting Alembic.

---

## Related

- ADR 0005 — dev tooling selection (the tools that pre-commit would automate are already chosen)
- `docs/architecture-design.md` — Section 9 (AWS future-state) describes the database migration that will require Alembic
- Future ADR (TBD) — adopt CI pipeline + pre-commit
- Future ADR (TBD) — adopt Alembic at first significant schema change
