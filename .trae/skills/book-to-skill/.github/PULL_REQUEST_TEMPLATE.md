<!-- Conventional Commit title, e.g. fix(extractor): scan full text -->

## What & why
<!-- What does this change and what problem does it solve? -->

## Evidence
<!-- Required for any claimed gain. A test, a discovery_tax.py number, or a
     before/after. "No behavior change" is a valid answer for pure docs/refactor. -->

## Checklist
- [ ] One focused change
- [ ] Tests added/updated for behavior changes
- [ ] `ruff check .` clean
- [ ] `pytest -q` green
- [ ] `python3 tools/validate_skill.py SKILL.md` passes (if SKILL.md changed)
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] No raw book text shipped; no net SKILL.md bloat without justification
