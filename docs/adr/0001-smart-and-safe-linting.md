# 1. Smart & Safe Linting Strategy

Date: 2025-12-30

## Status

Accepted

## Context & Requirements

The project requires a development environment that maximizes velocity and functional correctness while minimizing friction. The previous linting configuration was seen as overly pedantic, flagging stylistic preferences (e.g., whitespace, line length) as errors that blocked commits.

### Requirements

1. **Functional Correctness**: The system must catch logical bugs, syntax errors, and undefined variables before code is committed.
2. **Zero Friction**: The developer should not be blocked by non-functional style complaints.
3. **Readability**: The codebase must remain readable and consistent (standard indentation, sorted imports) without manual effort interaction.
4. **Type Safety**: The system must enforce type correctness to prevent runtime errors.
5. **Cost & Efficiency**: Developer time should not be spent on manual formatting or fighting the linter about "pretty" code.

### Stakeholder Concerns

* **Security**: Ensuring that relaxation of rules does not eventually lead to vulnerable or buggy code.
* **Cost/Efficiency**: "Wasting tokens" or developer cycles on trivial style fixes is unacceptable.
* **Systemic Quality**: The codebase must not "rot" into an unreadable mess of mixed styles.

## Decision: "Smart & Safe" Strategy

We have adopted a hybrid "Smart & Safe" linting strategy that clearly separates **formatting** (automated) from **linting** (functional).

### 1. Auto-Formatting (The "Smart" Part)

We use automated tools to handle all stylistic concerns. The developer writes code, and the machine makes it pretty.

* **Tool**: `ruff format` and `isort` (via Ruff's `I` selector).
* **Configuration**:
  * `trailing-whitespace` and `end-of-file-fixer` are enabled in pre-commit.
  * Ruff is configured to auto-fix and format on save/commit.
* **Effect**: Code is always consistent. Imports are always sorted. The developer never manually formats.

### 2. Strict Type Checking (The "Safe" Part)

We enforce strict typing to catch architectural and logical flaws.

* **Tool**: `mypy`.
* **Configuration**: `disallow_untyped_defs = true`, `check_untyped_defs = true`.
* **Effect**: We prevent `NoneType` errors and interface mismatches at compile time.

### 3. Quiet Linting (The "Frictionless" Part)

We expressly disable stylistic linting rules. The "Linter" is restricted.

* **Tool**: `ruff check`.
* **Configuration**: `select = ["F", "I"]`.
  * **F (Pyflakes)**: Catches undefined variables, unused imports, syntax errors.
  * **I (Isort)**: Enforces import sorting (which is auto-fixed).
  * **Disabled**: `E` (Style), `W` (Warnings), `N` (Naming), etc.
* **Effect**: The linter never complains about line length or indentation. It only speaks up if the code is actually broken.

## Consequences

### Positive

* **Maximized Velocity**: Commits are never blocked by style nits.
* **High Thread Safety**: Strict typing ensures the application logic is sound.
* **Consistency**: The auto-formatter ensures a uniform codebase without human intervention.
* **Reduced Noise**: Error logs only show actionable bugs.

### Negative

* **Implicit Style**: We rely entirely on the formatter's defaults. If the formatter does something "ugly" but valid, we accept it.
* **Missing Imports**: The strict `F` rule for unused imports (`F401`) might occasionally remove an import during debugging if it's temporarily commented out.

## Compliance

This decision is implemented in:

* `.pre-commit-config.yaml`
* `pyproject.toml`
* `CONTRIBUTING.md`
