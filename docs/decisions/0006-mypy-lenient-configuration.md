# ADR 0006: mypy Configured in Lenient Mode

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Project owner

---

## Context

`mypy` is the type checker selected in ADR 0005. It can be configured along a spectrum from "lenient" (catch only blatant errors, ignore missing annotations) to "strict" (require type annotations everywhere, complain about every untyped library import, treat `None` with maximum suspicion).

A strict configuration provides the strongest safety guarantees but imposes a real friction cost: every function needs annotations, every external library without type stubs produces noise, and every nullable value requires explicit handling. For a project where the developer is new to type checkers (and where some dependencies — notably `yfinance` — ship without type stubs), strict mode would generate many warnings that obscure the genuinely useful ones.

A lenient configuration provides a meaningful subset of the safety benefit while staying out of the way until the developer chooses to engage more deeply with the type system.

---

## Decision

Configure mypy in lenient mode for v1, with the following settings in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
files = ["app"]
ignore_missing_imports = true
check_untyped_defs = true
warn_unused_ignores = true
warn_redundant_casts = true
```

Leave the strict-mode flags commented out in the file as documentation:

```toml
# Intentionally NOT enabled yet (these are the "strict" flags):
# disallow_untyped_defs = true
# disallow_incomplete_defs = true
# strict_optional = true
# no_implicit_optional = true
```

Plan to enable strict flags incrementally — one at a time, starting with the service-layer and adapter boundaries — as the codebase matures and the developer gains comfort with the type system.

---

## Alternatives Considered

### Alternative A: No type checking

Skip mypy entirely. Defer the decision to a future date.

**Rejected because:** even lenient mypy catches a meaningful class of bugs (calling a method that does not exist on an inferred type, passing the wrong number of arguments, returning a value of the wrong shape) for almost no developer cost. The marginal cost of including it lenient is negligible; the marginal benefit is real.

### Alternative B: Strict from day one

Enable all strict flags immediately. Force the codebase to be fully typed from the first commit.

**Rejected because:**
- Project owner is new to Python type checkers. Drowning in warnings on every file would create friction that discourages writing the application at all.
- The yfinance library has no type stubs; strict mode would treat every interaction with it as an error, requiring extensive `# type: ignore` comments throughout the adapter layer.
- The time spent fighting the type checker in the early phase would not be repaid by bug prevention, because the early phase has few bugs that types would catch.
- Strict can always be turned on later by uncommenting flags one at a time, fixing what they reveal incrementally. The reverse direction (relaxing strict mode after writing strictly-typed code) is also fine but offers no benefit over starting lenient.

### Alternative C: Check `tests/` and `scripts/` too

Configure `files = ["app", "tests", "scripts"]` to type-check everything.

**Rejected because:** test code and utility scripts often intentionally play loose with types (mock objects with arbitrary attributes, fixture factories returning unions, quick-and-dirty data prep). Type-checking them tends to generate noise that obscures real issues in `app/`. Starting with `app/` only is the lenient posture; expanding scope later is trivial if desired.

---

## Configuration Rationale (Per Setting)

### `python_version = "3.12"`

Tells mypy which Python version's type system rules to apply. Matches `requires-python` in `pyproject.toml`. Without this, mypy assumes the version of Python it was installed under, which may differ across machines.

### `files = ["app"]`

Restricts type checking to the application directory. Tests and scripts are excluded for the reasons in Alternative C above.

### `ignore_missing_imports = true`

The most important lenient flag. When mypy encounters an import from a library that has no type stubs (e.g., `yfinance`, parts of `apscheduler`), it treats the imported symbols as `Any` rather than raising an error. Without this flag, the project would be flooded with "library stubs not installed" errors. With it, those imports are simply opaque to the type checker — a controlled loss of safety at well-defined boundaries.

### `check_untyped_defs = true`

The most useful lenient flag. Even in functions without type annotations, mypy will infer types where it can and check the function body for inconsistencies. Provides genuine value to a developer who has not yet adopted annotations.

### `warn_unused_ignores = true`

If a `# type: ignore` comment is added to silence an error, and that error later goes away (library gets stubs, code is refactored), mypy will flag the now-unnecessary ignore. Prevents accumulation of "type-ignore debt."

### `warn_redundant_casts = true`

Same idea: catches `cast()` calls that have become unnecessary. Keeps the type system tidy.

### Strict flags left off

- **`disallow_untyped_defs`** would refuse functions without parameter and return-type annotations. Too aggressive for v1 when many small helpers can be perfectly clear without annotations.
- **`disallow_incomplete_defs`** would refuse functions that are partially annotated. Same reasoning.
- **`strict_optional`** would treat `None` as a distinct type that must be handled explicitly. Useful at boundaries; noisy in routine code.
- **`no_implicit_optional`** would refuse the older idiom where a parameter with default `None` was implicitly typed `Optional`. Best enabled together with `strict_optional`.

---

## Consequences

### Positive

- mypy provides a meaningful safety net from day one without disrupting development flow.
- The commented-out strict flags serve as embedded documentation: future-self knows exactly which knobs to turn when ready to tighten.
- Project owner can adopt type annotations gradually, starting at the layer boundaries (service interfaces, scoring function signatures, adapter return types) where they provide the most value.
- The Yahoo Finance adapter, where the project's risk concentrates, can be typed strictly without forcing the rest of the code to follow.

### Negative

- Lenient mode lets some bugs through that strict mode would catch. Accepted trade-off given the project owner's familiarity level.
- Future tightening will require fixing accumulated issues. The cost grows with codebase size, so the longer strictness is deferred, the more work it becomes. Mitigated by an explicit follow-up plan to revisit periodically.

### Follow-up Required

- Revisit configuration after first 500 lines of application code. Consider enabling `strict_optional` first.
- Consider enabling `disallow_untyped_defs` only for `app/services/` and `app/adapters/` initially, leaving the web layer and DAL more lenient. mypy supports per-module configuration.

---

## Related

- ADR 0005 — dev tooling selection (where mypy was chosen)
- `pyproject.toml` — `[tool.mypy]` section with active configuration
