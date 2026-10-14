## What and why

<!-- One or two sentences: the problem, and how this change addresses it. -->

## How it was verified

<!-- Tests added or changed, launch tests, evaluation runs (attach the result file), hardware checks. -->

## Checklist

- [ ] Conventional Commit title (`feat:`, `fix:`, `docs:`, ...)
- [ ] `bash scripts/docker_verify.sh` passes (lint, unit, integration, architecture)
- [ ] New topics, services or parameters are registered in `tools/companion_contracts.py`
- [ ] ADR added if this changes a design decision
- [ ] Evaluation re-run and results committed if perception behaviour changed
- [ ] CHANGELOG.md updated under "Unreleased"
